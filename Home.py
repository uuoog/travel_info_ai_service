import openai
import streamlit as st
from supabase import create_client

def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase_client = init_connection()


st.markdown(
    """
<style>
footer {
    visibility: hidden;
}
</style>
""",
    unsafe_allow_html=True,
)

openai.api_key = st.secrets.OPENAI_TOKEN
openai_model_version = "gpt-3.5-turbo-0613"

st.title("어디로 떠나시나요?🛫")
st.image("https://techmarket.airport.kr:6943/portal/img/01.jpg")


def request_chat_completion(prompt):
    response = openai.ChatCompletion.create(
    model = "gpt-3.5-turbo-0613",
    messages = [
        {"role": "system", "content": "당신은 유용한 도우미 입니다."},
        {"role": "user", "content": prompt}
    ]
)
    return response["choices"][0]["message"]["content"]

def generate_prompt(city, style, day, n):

    prompt = f"""
    여행지에 대한 정보를 {n}개 생성해주세요.
    여행지가 지구에 있는 도시나 관광지가 아니면 다시 질문하라고 해주세요.
    여행지를 방문하기 좋은 시기는 언제인지 작성해주세요.
    여행지에서 원하는 여행 스타일에 대한 정보를 작성해주세요.
    여행 기간이 주어지면 여행지의 여행 평균 비용이 얼마 인지 작성해주세요.
    주어진 여행 기간과 여행 스타일로 여행코스를 추천해주세요.
    구글맵 url을 주세요.
    
---
여행지: {city}
여행 스타일: {style}
여행 기간:{day}
---

"""
    return prompt.strip()

def write_prompt_result(prompt, result):
    response = supabase_client.table("prompt_results").insert(
        {
            "prompt": prompt,
            "result": result
        }
    ).execute()
    print(response)

with st.form("my_form"):
    city = st.text_input("여행 하고싶은 도시(필수)", placeholder="제주도")
    style = st.text_input("어떤 여행을 하고싶으 신가요?(필수)", placeholder="먹방")
    day = st.text_input("여행은 며칠 가실 예정인가요?(필수)", placeholder="3일")

    submitted = st.form_submit_button("Submit")
    if submitted:
        if not city:
            st.error("도시명을 입력해주세요.")
        if not style:
            st.error("원하시는 여행 유형을 입력해주세요.")
        if not day:
            st.error("예상 여행기간을 입력해주세요.")
        else:
            with st.spinner("AI 카피라이터가 답변을 작성 중입니다..."):
                prompt = generate_prompt(city, style, day, n=3)
                response = request_chat_completion(prompt)
                write_prompt_result(prompt, response)
                st.text_area(
                    label = "여행지 답변 결과",
                    value = response,
                    placeholder="아직 생성된 문구가 없습니다.",
                    height=200
                )
