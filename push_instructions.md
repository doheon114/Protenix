# Protenix 전체 디렉토리 푸시 방법

아래 명령어를 사용하여 전체 `/home/hu2/Protenix` 디렉토리를 GitHub에 푸시할 수 있습니다.

## 1. 로컬 저장소 초기화

```bash
cd /home/hu2/Protenix
git init
```

## 2. 원격 저장소 연결

```bash
git remote add origin https://github.com/doheon114/Protenix.git
```

## 3. 파일 추가 및 커밋

```bash
# 모든 파일 추가
git add .

# 커밋 생성
git commit -m "Initial commit: Full Protenix codebase"
```

## 4. 브랜치 설정 및 푸시

```bash
# 브랜치 이름을 main으로 설정
git branch -M main

# GitHub에 푸시 (GitHub 인증 정보 필요)
git push -u origin main
```

## 참고사항

- 용량이 큰 파일이나 데이터 파일은 `.gitignore`에 추가하는 것이 좋습니다.
- GitHub에서는 개별 파일이 100MB를 초과할 수 없으므로 큰 파일은 Git LFS를 사용해야 합니다.
- 푸시하기 전에 민감한 데이터나 개인 정보가 포함된 파일이 없는지 확인하세요.

## 대용량 파일 처리 (선택사항)

대용량 파일이 있다면 Git LFS(Large File Storage)를 사용하세요:

```bash
# Git LFS 설치 (필요시)
apt-get install git-lfs

# Git LFS 초기화
cd /home/hu2/Protenix
git lfs install

# 대용량 파일 추적 (예: *.pdb, *.sto 파일)
git lfs track "*.pdb"
git lfs track "*.sto"
git lfs track "*.pt"

# .gitattributes 파일 추가
git add .gitattributes
```

이후 일반적인 git 명령어로 커밋 및 푸시하면 됩니다.