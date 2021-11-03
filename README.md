#  SHOEKREAM Project

![shokreammain](https://user-images.githubusercontent.com/78721108/139569482-db28b424-c233-4df5-9520-4da68e528439.gif)

- PREMIUM BIIDINGS

## 🎇 팀명 : shoekream - 슈크림

> 의류 경매 서비스를 제공하는 [KREAM](https://kream.co.kr/)을 모티브로 제작하게 된 SHOE-KREAM 팀의 프론트엔드 레포지토리 입니다.
> 짧은 프로젝트 기간동안 개발에 집중해야 하므로 디자인/기획 부분만 클론했습니다.
> 개발은 초기 세팅부터 전부 직접 구현했으며, 백앤드와 연결하여 실제 사용할 수 있는 서비스 수준으로 개발할 수 있도록 2주간 고군분투 하였습니다.

### 프로젝트 선정이유
- 조사결과, 해당 사이트의 경매 입찰 기능과 결제 플로우, 차트 구현, 상품리스트 필터 구현 등 배울 점이 많다고 판단하여 선정하게 되었습니다.

## 📅 개발 기간 및 개발 인원

- 개발 기간 : 2021/10/18 ~ 2021/10/29
- 개발 인원 <br/>
 👨‍👧‍👦 **Front-End** 4명 : [김현진](https://github.com/71summernight), [박산성](https://github.com/p-acid), [이선호](https://github.com/sunhoh), [하상영](https://github.com/sangyouh) <br/>
- [Front-end github 링크](https://github.com/wecode-bootcamp-korea/25-2nd-SUNKREAM-frontend)<br/>
 👨‍👧‍👦 **Back-End** 3명 : [박치훈](https://github.com/chihunmanse), [양가현](https://github.com/chrisYang256), [송영록](https://github.com/crescentfull)<br/>
- [Back-end github 링크](https://github.com/wecode-bootcamp-korea/25-2nd-SUNKREAM-backend)

## 🎬 프로젝트 구현 영상

- 🔗 [영상 링크] : 추후 재업데이트 예정

## ⚙ 적용 기술
- **Front-End** : HTML5, CSS3, React, SASS, JSX
- **Back-End** : Python, Django, MySQL, jwt, bcypt, AWS RDS, AWS EC2
- **Common** : Git, Github, Slack, Trello, Postman or Insomnia

## 🗜 [데이터베이스 Diagram(클릭 시 해당 링크로 이동합니다)](https://www.erdcloud.com/d/6Kq4rCsrgRkjcfZxk)
![kream](https://user-images.githubusercontent.com/78721108/139569506-39104ecf-7060-4aa0-8d45-c834bc1a4174.png)

## 💻 구현 기능
### BACKEND
#### 박치훈

> 입찰 결제
- 입찰 생성
- 구매/판매 사이즈별 입찰가 조회
- 주문 페이지에서 즉시 거래가 조회
- 주문 생성
- 상품 시세 조회
- 마이페이지에서 주문, 입찰 내역 조회


#### 양가현

> 소셜 로그인
- kakao social login / singup을 구현했습니다.
- 우리 서비스에 부합하는 회원정보만을 kakao로부터 response받습니다.
- 홈페이지 구조상 소셜로그인 하는 유저는 회원가입 의도가 있음을 착안하여 
  비회원의 경우 회원가입이 자동으로 되도록 로직을 설계하였습니다.

> 관심상품
- 관심상품에 대한 페이지는 둘로 나누어져 있고 동일한 API를 사용하도록 하였습니다.
- 상품 상세페이지 재 진입시 해당 상품에 대한 관심상품 등록정보가 필요하여
  유저-상품 중간테이블을 조회하여 FE에게 True/False값을 전달해 주었습니다.

#### 송영록
- > 상세 페이지
-
- > 상품 리스트
- 

## ❗ Reference
- 이 프로젝트는 [KREAM](https://kream.co.kr/) 사이트를 참조하여 학습목적으로 만들었습니다.
- 실무수준의 프로젝트이지만 학습용으로 만들었기 때문에 이 코드를 활용하여 이득을 취하거나 무단 배포할 경우 법적으로 문제될 수 있습니다.
- 이 프로젝트에서 사용하고 있는 사진 모두는 copyright free 사이트들의 이미지들을 취합 및 canva 에서 직접 제작한 이미지들로 제작되었습니다.
