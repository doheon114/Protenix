#!/usr/bin/env python3
"""
Stockholm 형식으로 MSA 데이터를 변환하는 유틸리티 스크립트
"""

import os
import sys
import argparse
from typing import List, Dict, Tuple

def fasta_to_stockholm(fasta_file: str, output_file: str) -> None:
    """FASTA 파일을 Stockholm 형식으로 변환합니다."""
    sequences = []
    identifiers = []
    current_seq = ""
    current_id = ""
    
    # FASTA 파일 읽기
    with open(fasta_file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('>'):
                if current_id and current_seq:
                    sequences.append(current_seq)
                    identifiers.append(current_id)
                current_id = line[1:].strip()
                current_seq = ""
            else:
                current_seq += line
    
    # 마지막 시퀀스 추가
    if current_id and current_seq:
        sequences.append(current_seq)
        identifiers.append(current_id)
    
    # Stockholm 파일 작성
    with open(output_file, 'w') as f:
        f.write("# STOCKHOLM 1.0\n\n")
        for i, (seq_id, seq) in enumerate(zip(identifiers, sequences)):
            # 첫 번째 시퀀스를 쿼리로 지정
            if i == 0:
                f.write("{:<40} {}\n".format("query", seq))
            else:
                f.write("{:<40} {}\n".format(seq_id, seq))
        f.write("//\n")
    
    print(f"변환 완료: {len(sequences)}개의 시퀀스가 {output_file}에 저장되었습니다.")

def main():
    parser = argparse.ArgumentParser(description='FASTA 파일을 Stockholm 형식으로 변환합니다.')
    parser.add_argument('fasta_file', type=str, help='입력 FASTA 파일 경로')
    parser.add_argument('--output', '-o', type=str, default='output.sto', help='출력 Stockholm 파일 경로')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.fasta_file):
        print(f"오류: 파일을 찾을 수 없습니다: {args.fasta_file}")
        sys.exit(1)
    
    fasta_to_stockholm(args.fasta_file, args.output)

if __name__ == "__main__":
    main()