# RNA MSA 예제 사용 가이드

이 문서는 Protenix에서 RNA MSA를 사용하는 방법을 설명합니다.

## 디렉토리 구조

RNA MSA 데이터는 다음과 같은.폴더 구조를 따릅니다:

```
examples/
├── R1107/
│   └── msa/
│       └── 1/
│           ├── non_pairing.sto (Stockholm 포맷 MSA 파일)
│           └── tosto.py (FASTA에서 Stockholm 변환 유틸리티)
├── R1108/
│   └── msa/
│       └── 1/
│           └── non_pairing.sto
└── ... (기타 RNA 구조)
```

## 사용 방법

### 1. 새로운 RNA MSA 추가하기

1. 새 RNA 구조에 대한 디렉토리 생성:
   ```bash
   mkdir -p examples/R<NUMBER>/msa/1
   ```

2. RNA MSA 데이터를 Stockholm 형식으로 준비:
   - 기존 RNA MSA 데이터가 FASTA 형식인 경우, `tosto.py` 스크립트로 변환:
     ```bash
     python examples/R1107/msa/1/tosto.py your_msa.fasta -o examples/R<NUMBER>/msa/1/non_pairing.sto
     ```
   - 또는 직접 Stockholm 형식 파일 작성 (형식 예제는 R1107 참고)

3. `example_all.json` 파일에 새 RNA 구조 추가:
   ```json
   {
     "sequences": [
       {
         "rnaSequence": {
           "sequence": "YOUR_RNA_SEQUENCE",
           "count": 1,
           "msa": {
             "precomputed_msa_dir": "./examples/R<NUMBER>/msa/1",
             "pairing_db": "uniref100"
           }
         }
       }
     ],
     "name": "R<NUMBER>"
   }
   ```

### 2. RNA MSA 추론 실행

```bash
bash inference_rna_demo.sh
```

## Stockholm 파일 형식

기본 Stockholm 형식은 다음과 같습니다:

```
# STOCKHOLM 1.0

query                GGGGGCCACAGCAGAAGCGUUCACGUCGCAGCCCCUGUCAGCCAUUGCACUCCGGCUGCGAAUUCUGCU
sequence1            GGGGGCCACAGCAGAAGCGUUCACGUCGCGGCCCCUGUCAG--AUUCUGGUGAAUCUGCGAAUUCUGCU
sequence2            GGGGGCCACAGCAGAAGCGUUCACGUCGCAGCCCCUGUCAG--AUUCUGGUGAAUCUGCGAAUUCUGCU
//
```

- 첫 번째 시퀀스는 항상 `query`로 표시되어야 합니다.
- 각 시퀀스는 이름과 시퀀스로 구성됩니다.
- 파일 끝에는 `//`를 포함해야 합니다.

## 문제 해결

- **MSA 토큰화 오류**: MSA와 토큰 배열 간 매핑에 실패하는 경우, 개선된 매핑 알고리즘이 자동으로 적용됩니다.
- **파일 크기 문제**: 대용량 MSA 파일은 청크 단위로 처리됩니다.
- **시퀀스 길이 불일치**: 시퀀스 길이가 다른 경우 자동으로 정규화됩니다.

## 참고 자료

- [Stockholm 포맷 명세](https://en.wikipedia.org/wiki/Stockholm_format)
- [RNA MSA 데이터베이스 - Rfam](https://rfam.org/)
- [RNA 구조 예측 가이드라인](https://rnacentral.org/)