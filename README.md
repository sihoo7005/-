# 파란 추진 불꽃 우주선

은색 우주선이 앞쪽(+X)으로 일정한 속도로 이동합니다. 두 추진기의 파란 불꽃은 길이가 조금씩 변합니다. 배경, 바닥, 별은 없습니다. 카메라는 고정되어 있어 우주선의 이동이 보입니다.

4초 · 초당 24프레임 · 640 × 480 · 투명 배경.

## 실행

블렌더가 설치된 리눅스에서:

```sh
git clone https://github.com/sihoo7005/-.git spaceship
cd spaceship
blender --background --python spaceship.py
```

`output/spaceship.blend`가 만들어집니다. 블렌더로 열고 타임라인을 재생하세요. 화면에서 투명 영역이 검게 보여도 출력 이미지는 투명합니다.

한 장 먼저 렌더링:

```sh
blender --background --python spaceship.py -- --preview
```

결과: `output/preview.png`.

전체 애니메이션 렌더링:

```sh
blender --background --python spaceship.py -- --render
```

결과: `output/frame_0001.png` - `output/frame_0096.png`. PNG(Portable Network Graphics) 이미지의 알파 채널에 투명도가 저장됩니다. 일반 MP4(MPEG-4 Part 14) 영상으로 바꾸면 보통 투명도가 사라지므로, 합성할 때는 이미지 시퀀스를 사용하세요.

## 안드로이드 리눅스

Termux의 Ubuntu·Debian 안에서 기기에 맞는 블렌더 패키지가 필요합니다. 저장소에 패키지가 있다면 `apt update` 후 `apt install blender`로 설치할 수 있습니다. 데스크톱 창을 열려면 Termux:X11과 호환되는 그래픽 설정이 필요합니다. `--background` 실행은 창을 열지 않습니다.

렌더링은 중앙처리장치(Central Processing Unit)를 사용합니다. 복잡한 연기 시뮬레이션 대신 가벼운 발광 메시로 불꽃을 표현합니다. 태블릿에서 96장 렌더링은 오래 걸릴 수 있으므로 미리보기부터 실행하세요.

스크립트는 실행 중인 블렌더 장면의 객체를 지웁니다. 새 파일에서 실행하세요. 블렌더 3.6 이상을 대상으로 작성했으며, 작성 환경에 블렌더가 없어 실제 실행과 렌더링은 아직 검증하지 못했습니다.
