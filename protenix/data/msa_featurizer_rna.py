# Copyright 2024 ByteDance and/or its affiliates.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import os
import logging
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import torch
from biotite.structure import AtomArray

from protenix.data.constants import rna_order_with_x
from protenix.data.msa_utils import (
    FeatureDict,
    load_and_process_msa,
    make_sequence_features,
    merge_features_from_prot_rna,
)
from protenix.data.tokenizer import TokenArray
from protenix.openfold_local.data.parsers import parse_stockholm

logger = logging.getLogger(__name__)

class RNAMSAFeaturizer:
    """RNA MSA 처리를 위한 클래스"""
    
    @staticmethod
    def process_rna_single_sequence(
        sequence: str, 
        description: str,
        is_homomer_or_monomer: bool,
        msa_dir: str
    ) -> FeatureDict:
        """단일 RNA 시퀀스 처리 및 MSA 특성 생성"""
        try:
            msa_feature = make_sequence_features(sequence, description, 'rna')
            
            if msa_dir and os.path.exists(msa_dir):
                raw_msa_path = {}
                
                # Stockholm 파일 경로 설정
                sto_path = os.path.join(msa_dir, "non_pairing.sto")
                if os.path.exists(sto_path):
                    raw_msa_path["rfam"] = sto_path
                    
                if raw_msa_path:
                    # Stockholm 파일 로드 및 처리
                    try:
                        msa_data = load_and_process_msa(
                            raw_msa_path,
                            sequence,
                            {"rfam": -1},
                            16384,
                            is_homomer_or_monomer
                        )
                        msa_feature.update(msa_data)
                    except Exception as e:
                        logger.warning(f"Error loading MSA data: {e}")
                else:
                    logger.warning(f"No MSA files found in directory: {msa_dir}")
            else:
                logger.warning(f"MSA directory not found: {msa_dir}")
                
            return msa_feature
            
        except Exception as e:
            logger.error(f"Error processing RNA sequence: {e}")
            # 기본 특성 반환
            return make_sequence_features(sequence, description, 'rna')
    
    @staticmethod
    def get_inference_rna_msa_features_for_assembly(
        bioassembly: Dict[str, Any],
        entity_to_asym_id: Dict[str, List[Union[int, str]]]
    ) -> Optional[FeatureDict]:
        """RNA MSA 특성 추출 메서드"""
        try:
            rna_entity_ids = {
                entity_id 
                for entity_id, poly_type in bioassembly["entity_poly_type"].items()
                if "polyribonucleotide" in poly_type
            }
            
            if not rna_entity_ids:
                logger.info("No RNA entities found in bioassembly")
                return None
                
            # RNA 엔티티만 필터링
            filtered_entity_to_asym_id = {
                k: v for k, v in entity_to_asym_id.items() if k in rna_entity_ids
            }
            
            if not filtered_entity_to_asym_id:
                logger.info("No RNA asym_ids found in entity_to_asym_id mapping")
                return None
                
            # RNA 시퀀스 데이터 수집
            sequences = bioassembly["sequences"]
            rna_sequences = {
                entity_id: seq for entity_id, seq in sequences.items() 
                if entity_id in rna_entity_ids
            }
            
            if not rna_sequences:
                logger.info("No RNA sequences found in bioassembly")
                return None
                
            # MSA 데이터 수집
            msa_features_list = []
            for entity_id, asym_ids in filtered_entity_to_asym_id.items():
                if entity_id not in rna_sequences:
                    continue
                    
                sequence = rna_sequences[entity_id]
                description = f"entity_{entity_id}"
                
                # RNA MSA 디렉토리 확인
                msa_dir = None
                if "rna_msa_dirs" in bioassembly and entity_id in bioassembly["rna_msa_dirs"]:
                    msa_dir = bioassembly["rna_msa_dirs"][entity_id]
                
                is_homomer = len(asym_ids) > 1
                msa_feature = RNAMSAFeaturizer.process_rna_single_sequence(
                    sequence, description, is_homomer, msa_dir
                )
                
                if msa_feature:
                    msa_features_list.append(msa_feature)
            
            if not msa_features_list:
                logger.warning("No RNA MSA features could be generated")
                return None
                
            # MSA 데이터 병합
            merged_features = merge_features_from_prot_rna(msa_features_list, "rna")
            logger.info(f"Successfully generated RNA MSA features for {len(msa_features_list)} entities")
            return merged_features
            
        except Exception as e:
            logger.error(f"Error generating RNA MSA features: {e}")
            return None
            
    @staticmethod
    def tokenize_msa(msa_feats, token_array, atom_array):
        """MSA 데이터 토큰화 메서드"""
        try:
            if not msa_feats:
                logger.warning("Empty MSA features provided for tokenization")
                return None
                
            required_keys = ["msa", "has_deletion", "deletion_value"]
            if not all(key in msa_feats for key in required_keys):
                logger.warning(f"MSA features missing required keys: {required_keys}")
                return None
                
            # 중심 원자 인덱스 가져오기
            center_indices = token_array.get_annotation("centre_atom_index")
            if center_indices is None or len(center_indices) == 0:
                logger.warning("No center atom indices found in token array")
                return None
                
            # residue ID를 MSA 인덱스에 매핑
            res_id_2_msa_idx = {}
            msa_idx = 0
            
            # 1-인덱스와 0-인덱스 모두 시도하여 매핑 성공률 향상
            for idx in range(len(atom_array)):
                atom = atom_array[idx]
                if hasattr(atom, "residue_id") and hasattr(atom, "asym_id"):
                    # 1-인덱스 매핑 (일부 RNA 구조에서 사용)
                    key_1based = (atom.asym_id, atom.residue_id)
                    # 0-인덱스 매핑 (일부 RNA 구조에서 사용)
                    key_0based = (atom.asym_id, atom.residue_id - 1)
                    
                    if atom.atom_name == "C4'" and atom.entity_id in msa_feats.get("entity_ids", []):
                        if key_1based not in res_id_2_msa_idx and key_0based not in res_id_2_msa_idx:
                            res_id_2_msa_idx[key_1based] = msa_idx
                            res_id_2_msa_idx[key_0based] = msa_idx
                            msa_idx += 1
            
            # 중심 원자 인덱스를 MSA 열에 매핑
            token_2_msa_col = []
            mapped_tokens = 0
            
            # 첫 몇 개 토큰의 상세 정보 로깅
            for i, center_idx in enumerate(center_indices[:5]):
                atom = atom_array[center_idx]
                if hasattr(atom, "residue_id") and hasattr(atom, "asym_id"):
                    logger.debug(f"Token {i}: asym_id={atom.asym_id}, res_id={atom.residue_id}, "
                                 f"atom_name={atom.atom_name}, entity_id={atom.entity_id}")
            
            for center_idx in center_indices:
                atom = atom_array[center_idx]
                if hasattr(atom, "residue_id") and hasattr(atom, "asym_id"):
                    key_1based = (atom.asym_id, atom.residue_id)
                    key_0based = (atom.asym_id, atom.residue_id - 1)
                    
                    if key_1based in res_id_2_msa_idx:
                        token_2_msa_col.append(res_id_2_msa_idx[key_1based])
                        mapped_tokens += 1
                    elif key_0based in res_id_2_msa_idx:
                        token_2_msa_col.append(res_id_2_msa_idx[key_0based])
                        mapped_tokens += 1
                    else:
                        token_2_msa_col.append(-1)
            
            # 매핑 실패 시 순차적 매핑 시도
            if mapped_tokens == 0:
                logger.warning("No residues could be mapped between MSA and token array. "
                              "Trying sequential mapping as fallback.")
                token_2_msa_col = list(range(min(len(center_indices), msa_feats["msa"].shape[1])))
                token_2_msa_col.extend([-1] * (len(center_indices) - len(token_2_msa_col)))
            
            # 토큰화된 MSA 특성 생성
            msa = msa_feats["msa"]
            msa_shape = msa.shape
            
            # RNA residue 타입 토큰화
            restypes = np.array([rna_order_with_x.index(res) for res in msa_feats.get("restypes", [])])
            if len(restypes) < len(token_2_msa_col):
                logger.warning(f"restypes ({len(restypes)}) is shorter than token_2_msa_col ({len(token_2_msa_col)})")
                restypes = np.pad(restypes, (0, len(token_2_msa_col) - len(restypes)), constant_values=len(rna_order_with_x)-1)
            
            # MSA 특성 구성
            tokenized_msa = {
                "msa_seed_orig_restypes": restypes,
                "msa_rows": msa_shape[0],
                "msa_cols": len(token_2_msa_col),
                "token_2_msa_col": np.array(token_2_msa_col),
            }
            
            # MSA 속성 처리
            for msa_attr in ["msa", "has_deletion", "deletion_value"]:
                if msa_attr in msa_feats:
                    tokenized_msa[msa_attr] = msa_feats[msa_attr]
            
            # deletion_mean 계산
            if "deletion_value" in msa_feats and "has_deletion" in msa_feats:
                deletion_value = msa_feats["deletion_value"]
                has_deletion = msa_feats["has_deletion"]
                
                deletion_mean = np.zeros((msa_shape[1],))
                for i in range(msa_shape[1]):
                    deletion_mean[i] = np.sum(
                        deletion_value[:, i] * has_deletion[:, i]) / (np.sum(has_deletion[:, i]) + 1e-10)
                tokenized_msa["deletion_mean"] = deletion_mean
            
            # profile 처리
            if "profile" in msa_feats:
                tokenized_msa["profile"] = msa_feats["profile"]
            
            logger.info(f"Successfully tokenized MSA with shape {msa_shape}, mapped {mapped_tokens}/{len(center_indices)} tokens")
            return tokenized_msa
            
        except Exception as e:
            logger.error(f"Error tokenizing MSA: {e}")
            return None

def make_msa_feature(bioassembly, entity_to_asym_id, token_array, atom_array):
    """RNA와 단백질 MSA 특성 통합 메서드"""
    try:
        # RNA MSA 특성 추출
        rna_msa_features = RNAMSAFeaturizer.get_inference_rna_msa_features_for_assembly(
            bioassembly, entity_to_asym_id
        )
        
        if rna_msa_features:
            logger.info(f"Generated RNA MSA features with shape: {rna_msa_features.get('msa', {}).shape}")
            # RNA MSA 특성 토큰화
            msa_features = RNAMSAFeaturizer.tokenize_msa(rna_msa_features, token_array, atom_array)
            if msa_features:
                logger.info("Successfully generated tokenized RNA MSA features")
                return msa_features
            else:
                logger.warning("Failed to tokenize RNA MSA features")
        else:
            logger.info("No RNA MSA features generated")
        
        # 특성 생성 실패 시 기본값 반환
        return None
    except Exception as e:
        logger.error(f"Error in make_msa_feature: {e}")
        return None