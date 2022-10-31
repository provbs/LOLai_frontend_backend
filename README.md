# LOLai_frontend_backend

# LOLai - frontend + backend

![image](https://user-images.githubusercontent.com/97097656/199012714-a61f748c-7b41-4dc5-8c50-b2d3c9992573.png)


2022.06월 (1인 프로젝트)

누구나 한번쯤은 꿈꿔보는, 인공지능을 사용한 주식 트렌드 예측 프로그램을 개발해 보았습니다. 몇 년 전부터 주식에 관심이 많았던 만큼, 상당히 많은 증권회사에서 AI를 활용한 주식 예측 프로그램을 개발 혹은 서비스 중임을 알고 있었고, 직접 개발해 본다면 어느 정도의 효율을 낼 수 있을까 궁금한 마음에 시작하게 되었습니다.

개발은 Google Colab에서 진행하였으며, python 언어로 Tensorflow를 사용하여 머신러닝을 진행하였습니다.
Sklearn의 셔플기능을 사용해서 머신러닝의 오류를 최소화하려고 해보았으며,  metaplotlib를 사용해서 예상 결과값을 실제값과 비교하여 제 모델이 얼마만큼의 효율성을 가지는지 확인해 보았습니다.

개인적으로 현재 인터넷에서 쉽게 찾아볼 수 있는 linear regression을 사용한 주식분석에는 한계가 있다고 생각하여, 전날, 혹은 저번 주, 혹은 저번 달이 현재의 주가에 영향을 미치는 만큼, 시계열 데이터와 동일하게 LSTM과 같은 RNN방식의 모델을 사용해 봄이 의미가 있다 생각하였습니다.

여러 방식으로 데이터를 전처리하여 학습을 진행하였으며, Many to One, Many to Many, One to One 방식으로 다양한 방식의 접근을 시도해보았습니다.  머신러닝을 사용하여 원하는 결과 값을 얻기 위해, 어떤 식으로 데이터를 처리하여야 하고, 어떤 방식으로 학습을 해야 하는가에 대한 고민을 통해 인공지능 모델 설계에 대한 이해도를 높일 수 있었던 경험이었다 생각합니다.
