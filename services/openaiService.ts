import OpenAI from "openai";
import { AIAnalysis } from "../types";

const getClient = () => {
  const apiKey = process.env.API_KEY;
  if (!apiKey) {
    throw new Error("API_KEY not found in environment variables");
  }
  return new OpenAI({ apiKey, dangerouslyAllowBrowser: true });
};

export const analyzeTender = async (tenderText: string): Promise<AIAnalysis> => {
  try {
    const client = getClient();
    
    const response = await client.chat.completions.create({
      model: "gpt-4o-mini",
      response_format: { type: "json_object" },
      messages: [
        {
          role: "system",
          content: "You are an expert analyst for construction and service tenders. Always respond with valid JSON."
        },
        {
          role: "user",
          content: `Analyze the following construction/service tender text for a general contractor.
      
Tender Text: "${tenderText}"
      
Provide a JSON object with:
- summary: A concise 2-sentence summary of the work required.
- relevanceScore: A number from 0 to 100.
- keyRisks: An array of strings listing potential risks or challenging requirements.
- recommendation: One of "STRONG_BID", "POSSIBLE", or "IGNORE".
      
Return only valid JSON, no other text.`
        }
      ],
      temperature: 0.3
    });

    const content = response.choices[0]?.message?.content;
    if (content) {
      return JSON.parse(content) as AIAnalysis;
    }
    
    throw new Error("No response content from OpenAI");

  } catch (error) {
    console.error("Error analyzing tender:", error);
    return {
      summary: "AI Analysis failed. Please try again.",
      relevanceScore: 0,
      keyRisks: ["Analysis unavailable"],
      recommendation: "POSSIBLE"
    };
  }
};

