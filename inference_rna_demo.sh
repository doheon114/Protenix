#!/bin/bash
# RNA MSA 기능이 포함된 추론 데모 스크립트

# 스크립트 작동 위치 설정
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd $SCRIPT_DIR

# 환경 변수 설정
export PYTHONPATH=$SCRIPT_DIR:$PYTHONPATH

# 입력 및 출력 경로 설정
input_json_path="./examples/example_all.json"
dump_dir="./output/rna_inference_demo"

# 데이터 타입 설정 (fp32 또는 bf16)
dtype="fp32"

# 옵션 설정
use_msa=true          # MSA 사용 (RNA MSA 포함)
use_esm=false         # ESM 사용 안함

# 추론 실행
python runner/inference.py \
    --input_json_path $input_json_path \
    --dump_dir $dump_dir \
    --seed 42 \
    --dtype $dtype \
    --use_msa $use_msa \
    --use_esm $use_esm

echo "RNA MSA 추론이 완료되었습니다. 결과는 $dump_dir 디렉토리에 저장되었습니다."