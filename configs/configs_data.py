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

import os

# 데이터 루트 디렉토리 설정
DATA_ROOT_DIR = os.environ.get("PROTENIX_DATA_DIR", "./data")

# MSA 관련 설정
msa_config = {
    "msa": {
        "enable_msa": True,
        "enable_rna_msa": True,  # RNA MSA 활성화
        "use_templates": False,
        "msa_mode": "single_sequence",
        "msa_dir": os.path.join(DATA_ROOT_DIR, "msa"),
        "rna_msa_dir": os.path.join(DATA_ROOT_DIR, "rna_msa"),  # RNA MSA 디렉토리
        "max_msa_sequences": 512,
        "max_extra_msa": 1024,
        "max_hits": 10000,
        "path": {
            "uniref90": os.path.join(DATA_ROOT_DIR, "uniref90"),
            "mgnify": os.path.join(DATA_ROOT_DIR, "mgnify"),
            "uniprot": os.path.join(DATA_ROOT_DIR, "uniprot"),
            "rnacentral": os.path.join(DATA_ROOT_DIR, "rnacentral"),  # RNA 시퀀스 데이터베이스
            "rfam": os.path.join(DATA_ROOT_DIR, "rfam"),  # Rfam RNA 데이터베이스
        },
        "index": {
            "mmseqs_uniref90": os.path.join(DATA_ROOT_DIR, "mmseqs_uniref90"),
            "mmseqs_uniref30": os.path.join(DATA_ROOT_DIR, "mmseqs_uniref30"),
            "mmseqs_uniprot": os.path.join(DATA_ROOT_DIR, "mmseqs_uniprot"),
            "mmseqs_rfam": os.path.join(DATA_ROOT_DIR, "mmseqs_rfam"),  # Rfam 인덱스
            "mmseqs_rnacentral": os.path.join(DATA_ROOT_DIR, "mmseqs_rnacentral"),  # RNAcentral 인덱스
        },
        "tool": {
            "hhblits": "hhblits",
            "hhsearch": "hhsearch",
            "jackhmmer": "jackhmmer",
            "hmmsearch": "hmmsearch",
            "hmmbuild": "hmmbuild",
            "cmalign": "cmalign",  # RNA 구조 정렬 도구
            "mmseqs": "mmseqs",
        },
        "database": {
            "pdb": {
                "mmcif_dir": os.path.join(DATA_ROOT_DIR, "pdb_mmcif", "mmcif_files"),
                "mmcif_obsolete_dir": os.path.join(DATA_ROOT_DIR, "pdb_mmcif", "obsolete"),
                "seq_to_pdb_idx_path": os.path.join(DATA_ROOT_DIR, "seq_to_pdb_index.json"),
                "seq_to_structure_path": os.path.join(DATA_ROOT_DIR, "seq_to_structure.db"),
            },
            "rfam": {
                "seq_to_pdb_idx_path": os.path.join(DATA_ROOT_DIR, "rna_seq_to_pdb_index.json"),  # RNA 시퀀스-구조 매핑
            },
        },
        "seq_db": ["uniref90", "mgnify", "uniprot", "rnacentral", "rfam"],
        "msa_binary_fields": [
            "msa",
            "has_deletion",
            "deletion_value",
            "msa_mask",
            "deletion_mean",
            "target_feat",
            "target_mask",
            "msa_feat",
        ],
        "max_chunk": 4096,  # 큰 MSA 파일 처리 청크 크기
        "max_chunk_residue": 512,  # 레지듀 청크 크기
    },
    "protein_feature": {
        "enable_monomer_feature": True,
        "use_primitive_features": True,  # 기본 특성 사용
    },
    "rna_feature": {
        "enable_rna_feature": True,  # RNA 특성 활성화
        "use_primitive_features": True,  # 기본 특성 사용
    },
}

# ESM 설정
esm_config = {
    "enable_esm": False,
    "model_version": os.path.join(DATA_ROOT_DIR, "esm2", "esm2_t36_3B_UR50D.pt"),
    "model_name": "esm2_t36_3B_UR50D",
    "token_path": os.path.join(DATA_ROOT_DIR, "esm2", "tokenizer.json"),
    "batch_size": 1024,
    "max_str_len": 1023,  # ESM2 최대 길이 (계산 효율성을 위해)
}

# 데이터 처리 설정
preprocess_config = {
    "num_workers": {
        "train": 3,
        "val": 2,
        "test": 2,
    },
    "batch_size": {
        "train": 1,
        "val": 1,
        "test": 1,
    },
    "pin_memory": True,
    "add_pdb_structure": True,  # 실험적 특성
}

# 최종 데이터 설정
DATA_CONFIG = {
    "random_seed": 0,
    "num_workers": 4,
    "data_dir": DATA_ROOT_DIR,
    "msa": msa_config["msa"],
    "esm": esm_config,
    "preprocess": preprocess_config,
    "protein_feature": msa_config["protein_feature"],
    "rna_feature": msa_config["rna_feature"],  # RNA 특성 설정 추가
}