// 04-3. JavaScript(OpenAI Node SDK)로 Gateway 호출하기
// 실행: npm install openai && node client.mjs
import OpenAI from "openai";

const client = new OpenAI({
  baseURL: process.env.LITELLM_BASE_URL ?? "http://localhost:4000",
  apiKey: process.env.LITELLM_MASTER_KEY,
});

for (const model of ["fast", "smart", "gemini"]) {
  const response = await client.chat.completions.create({
    model,
    messages: [{ role: "user", content: "한 단어로: 맑은 하늘의 색은?" }],
  });
  console.log(`${model}: ${response.choices[0].message.content}`);
}
