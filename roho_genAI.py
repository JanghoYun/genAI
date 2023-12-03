##### 기본 정보 입력 #####
import streamlit as st
# OpenAI 패키기 추가
import openai
# 인스타그램 패키기 추가
from instagrapi import Client
#이미지 처리
from PIL import Image
import urllib
#구글 번역
from googletrans import Translator

##### 기능 구현 함수 #####
# 영어로 번역
def google_trans(messages):
    google = Translator()
    result = google.translate(messages, dest="en")

    return result.text

#질문하기
def askGPT(prompt):
    message_prompt =[{"role":"system", "content":prompt}]
    response = openai.ChatCompletion.create(model='gpt-3.5-turbo',messages=message_prompt)
    getresponse = response["choice"][0],["message"]["content"]
    return getresponse


# 인스타 업로드
def uploadinstagram(description):
    cl = Client()
    cl.login(st.session_state["instagram_ID"], st.session_state["instagram_Password"])
    cl.photo_upload("instaimg_resize.jpg" , description)

# ChatGPT에게 질문/답변받기
def getdescriptionFromGPT(topic, mood):
    prompt = f'''
Write me the Instagram post description or caption in just a few sentences for the post 
-topic : {topic}
-Mood : {mood}
Format every new sentence with new lines so the text is more readable.
Include the best Instagram hashtags for that post.
Hashtags should be placed at the end. 
The first caption sentence should hook the readers.
write all output in korean.'''
    messages_prompt = [{"role": "system", "content": prompt}]
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages_prompt)

    system_message = response["choices"][0]["message"]
    return system_message["content"]

# DALLE.2에게 질문/그림 URL 받기
def getImageURLFromDALLE(topic,mood):
    t_topic = google_trans(topic)
    t_mood = google_trans(mood)
    prompt_ = f'Draw picture about {t_topic}. picture Mood is {t_mood}.Draw the picture as close to a real photo as possible.Draw with an emotional feel that will become a hot topic on social media.'
    print(prompt_)
    response = openai.Image.create(
        prompt=prompt_,
        n=1,
        size="1024x1024",
        model ="dall-e-3",
        

        )

    image_url = response['data'][0]['url']
    urllib.request.urlretrieve(image_url, "instaimg.jpg")

##### 메인 함수 #####
def main():


    # 기본 설정
    st.set_page_config(page_title="로호네 Gen.AI 사용하기", page_icon="?")

    # 사이드바 바 생성
    with st.sidebar:

        # Open AI API 키 입력받기
        open_apikey = st.text_input(label='OPENAI API 키', placeholder='Enter Your API Key', value='',type="password")

        # 입력받은 API 키 표시
        if open_apikey:
            openai.api_key = open_apikey    
        

        st.markdown('---')


    tab1,tab2 = st.tabs(["인스타 post 하기", "리뷰쓰기"])
    with tab1:

        # session state 초기화
        if "description" not in st.session_state:
             st.session_state["description"] = ""

        if "flag" not in st.session_state:
            st.session_state["flag"] = False

        if "instagram_ID" not in st.session_state:
            st.session_state["instagram_ID"] = ""

        if "instagram_Password" not in st.session_state:
            st.session_state["instagram_Password"] = ""

        # 제목 
        st.header('인스타그램   생성기')
        # 구분선
        st.markdown('---')

        # 기본 설명
        with st.expander("인스타그램 생성기 사용방법", expanded=True):
            st.write(
            """     
            - 주제에 최대한 자세히 상세하게 설명해주면 좋습니다.
            - 이미지는 OpenAI의 Dall.e 3 를 활용하여 생성합니다. 
            - 너무 많이 업로드하면 instagram에서 IP Ban 을 하는데 VPN을 사용하면 좋습니다
            """
             )

            st.markdown("")

   
        topic = st.text_input(label="주제", placeholder="축구, 인공지능...")
        mood = st.text_input(label="분위기 (e.g. 재미있는, 진지한, 우울한)",placeholder="재미있는")

        if st.button(label="생성",type="secondary") and not st.session_state["flag"]:

            with st.spinner('생성 중'):
                st.session_state["description"] = getdescriptionFromGPT(topic,mood)
                getImageURLFromDALLE(topic,mood)
                st.session_state["flag"] = True

        if st.session_state["flag"]:
            image = Image.open('instaimg.jpg')  
            st.image(image)
            # st.markdown(st.session_state["description"])
            txt = st.text_area(label = "Edit Description",value  = st.session_state["description"],height=50)
            st.session_state["description"] = txt

            st.markdown('인스타그램 ID/PW')
            # 인스타그램 ID 입력받기
            st.session_state["instagram_ID"] = st.text_input(label='ID', placeholder='Enter Your ID', value='')
            # 인스타그램 비밀번호
            st.session_state["instagram_Password"] = st.text_input(label='Password',type='password', placeholder='Enter Your Password', value='')

            if st.button(label='업로드'):
                image = Image.open("instaimg.jpg")
                image = image.convert("RGB")
                new_image = image.resize((1080, 1080))
                new_image.save("instaimg_resize.jpg")
                uploadinstagram(st.session_state["description"])
                st.session_state["flag"] = False

    with tab2:
        st.header("리뷰문구 만들기")
        st.markdown('---')

        col1,col2 = st.columns(2)
        with col1:
            name =st.text_input("상품명")
            max_len = st.text_input("최대 리뷰글자수")
        with col2:
            feature = st.text_input("특징")
            tone_manner = st.text_input("톤앤매너",placeholder="감성적, 친절, 효도상품, 사용한것처럼 등")
            mustword = st.text_input("필수키워드")

        if st.button("리뷰문구 생성하기"):  
            prompt = f'''
            아래 내용을 참고해서 최대 {max_len} 글자 길이의 리뷰를 한글로 작성해줘
            - 상품명 : {name}
            - 특징 : {feature}
            - 톤앤매너 :{tone_manner}
            - 필수 포함 키워드 :{mustword}
            '''

            st.info(askGPT(prompt))

#    with tab3:
#        text = st.text_area("요약 할 글을 입력하세요")
#        if st.button("요약"):
#            prompt = f'''
#        **Instructions** :
#        - You are an expert assistant that summarizes text into **Korean language**.
#        - Your task is to summarize the **text** sentences in **Korean language**.
#        - Your summaries should include the following :
#        - Omit duplicate content, but increase the summary weight of duplicate content.
#        - Summarize by emphasizing concepts and arguments rather than case evidence.
#        - Summarize in 3 lines.
#        - Use the format of a bullet point.
#        -text : {text}
#        '''
#       st.info(askGPT(prompt))            

if __name__=="__main__":
    main()