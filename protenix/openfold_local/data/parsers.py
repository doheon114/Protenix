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

import re
import os
import logging
from typing import Dict, List, Optional, Tuple, Union, Any, Sequence

import numpy as np
from io import StringIO

logger = logging.getLogger(__name__)

class Msa:
    """MSA 클래스"""
    def __init__(
        self,
        sequences: List[str],
        descriptions: List[str],
        deletion_matrices: Optional[List[List[int]]] = None,
    ):
        """
        MSA 데이터를 위한 클래스

        Args:
            sequences: 정렬된 시퀀스 리스트
            descriptions: 시퀀스 설명 리스트
            deletion_matrices: 삭제 매트릭스 리스트
        """
        self.sequences = sequences
        self.descriptions = descriptions
        
        if deletion_matrices is None:
            deletion_matrices = []
            for sequence in sequences:
                deletion_matrix = []
                for symbol in sequence:
                    if symbol == "-":
                        deletion_matrix.append(0)
                    else:
                        deletion_matrix.append(0)
                deletion_matrices.append(deletion_matrix)
                
        self.deletion_matrices = deletion_matrices
        
        # 유효성 검사
        if len(self.sequences) != len(self.descriptions):
            raise ValueError(
                f"Sequence length {len(self.sequences)} != description length {len(self.descriptions)}"
            )
            
        if len(self.sequences) != len(self.deletion_matrices):
            raise ValueError(
                f"Sequence length {len(self.sequences)} != deletion matrix length {len(self.deletion_matrices)}"
            )
            
        for i, (seq, mtx) in enumerate(zip(self.sequences, self.deletion_matrices)):
            if len(seq) != len(mtx):
                raise ValueError(
                    f"Sequence {i} length {len(seq)} != deletion matrix {i} length {len(mtx)}"
                )

def parse_stockholm(
    stockholm_file: str, 
    max_sequences: int = 10000,
    chunk_size: int = 500
) -> Msa:
    """
    Stockholm 형식의 MSA 파일을 파싱합니다.
    
    Args:
        stockholm_file: Stockholm 파일 경로
        max_sequences: 최대 시퀀스 수 (기본값: 10000)
        chunk_size: 한 번에 처리할 시퀀스 수 (기본값: 500)
        
    Returns:
        파싱된 MSA 객체
    """
    try:
        # 파일이 존재하는지 확인
        if not os.path.exists(stockholm_file):
            logger.error(f"Stockholm file does not exist: {stockholm_file}")
            return Msa([""], [""])
            
        # 파일 크기 확인
        file_size = os.path.getsize(stockholm_file)
        logger.info(f"Parsing Stockholm file: {stockholm_file} (size: {file_size} bytes)")
        
        sequences = []
        descriptions = []
        
        with open(stockholm_file, "r") as f:
            # 첫 줄 확인 - Stockholm 형식이어야 함
            header = f.readline().strip()
            if not header.startswith("# STOCKHOLM"):
                logger.error(f"Invalid Stockholm format in file: {stockholm_file}")
                return Msa([""], [""])
                
            # 가독성을 위해 현재 시퀀스 카운터 초기화
            current_count = 0
            
            # 청크 기반 처리
            while current_count < max_sequences:
                chunk_sequences = []
                chunk_descriptions = []
                
                for _ in range(chunk_size):
                    line = f.readline()
                    if not line:
                        break
                        
                    line = line.strip()
                    
                    # 주석이나 빈 줄 건너뛰기
                    if not line or line.startswith("#"):
                        continue
                        
                    # 파일 끝 표시
                    if line == "//":
                        break
                        
                    # 시퀀스 라인 파싱
                    parts = re.split(r"\s+", line, 1)
                    if len(parts) != 2:
                        continue
                        
                    description, sequence = parts
                    
                    # 공백, 숫자 제거
                    sequence = re.sub(r'[\s\d]', '', sequence)
                    
                    chunk_descriptions.append(description)
                    chunk_sequences.append(sequence)
                
                # 청크 시퀀스 없으면 종료
                if not chunk_sequences:
                    break
                    
                # 메인 리스트에 추가
                sequences.extend(chunk_sequences)
                descriptions.extend(chunk_descriptions)
                
                # 카운터 업데이트
                current_count += len(chunk_sequences)
                
                # 최대 시퀀스 수 확인
                if current_count >= max_sequences:
                    logger.warning(f"Maximum sequences ({max_sequences}) reached. Truncating.")
                    break
        
        # 결과 확인
        if not sequences:
            logger.warning(f"No sequences found in Stockholm file: {stockholm_file}")
            return Msa([""], [""])
            
        logger.info(f"Successfully parsed {len(sequences)} sequences from Stockholm file")
        
        # 모든 시퀀스의 길이가 동일한지 확인
        if len(set(len(seq) for seq in sequences)) > 1:
            logger.warning("Sequences have different lengths in Stockholm file")
            
            # 첫 번째 시퀀스를 기준으로 다른 시퀀스의 길이 조정
            ref_len = len(sequences[0])
            for i in range(1, len(sequences)):
                if len(sequences[i]) < ref_len:
                    sequences[i] = sequences[i] + "-" * (ref_len - len(sequences[i]))
                elif len(sequences[i]) > ref_len:
                    sequences[i] = sequences[i][:ref_len]
            
        # 삭제 행렬 생성
        deletion_matrices = []
        for seq in sequences:
            deletion_matrix = [0 if char == "-" else 0 for char in seq]
            deletion_matrices.append(deletion_matrix)
            
        return Msa(sequences, descriptions, deletion_matrices)
        
    except Exception as e:
        logger.error(f"Error parsing Stockholm file {stockholm_file}: {str(e)}")
        return Msa([""], [""])