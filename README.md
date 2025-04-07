# Protenix with RNA MSA Support

이 저장소는 Protenix에 RNA MSA(Multiple Sequence Alignment) 기능을 추가한 확장 버전입니다.

## 주요 기능

- RNA 시퀀스에 대한 MSA 생성 및 처리 지원
- Stockholm 포맷 파일 파싱 기능 개선
- RNA MSA 토크나이징 알고리즘 개선
- 다양한 RNA 구조에 대한 예제 포함

## 파일 구조

- `protenix/data/msa_featurizer.py`: RNA MSA 처리 로직이 구현된 핵심 파일
- `protenix/data/msa_utils.py`: MSA 유틸리티 함수
- `examples/`: 다양한 RNA 구조 예제

## 사용법

```bash
# RNA MSA를 포함한 예제 파일로 예측 실행
protenix predict --input examples/example_all.json --out_dir ./output --seeds 101
```

## 지원되는 RNA 구조

- R1107부터 R1190까지의 다양한 RNA 구조 예제 지원
- 각 RNA 구조에 대한 MSA 데이터 포함

## 주의사항

- 이 버전은 RNA 구조 예측을 위한 실험적 기능을 포함하고 있습니다
- RNA MSA 처리를 위해서는 추가 데이터 파일이 필요할 수 있습니다