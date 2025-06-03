import { openai } from "@ai-sdk/openai"
import { streamText } from "ai"

// Allow streaming responses up to 30 seconds
export const maxDuration = 30

export async function POST(req: Request) {
  const { messages } = await req.json()

  const result = streamText({
    model: openai("gpt-4o"),
    messages,
    system: `Você é o CP Tracker, um assistente especializado em informações sobre comboios da CP (Comboios de Portugal).

Você tem acesso a informações sobre:
- Horários de comboios
- Estado das linhas e perturbações
- Informações de estações
- Preços e bilhetes
- Conexões e correspondências

Responda sempre em português de Portugal e seja útil, preciso e amigável. 
Quando não tiver informações específicas em tempo real, forneça informações gerais úteis sobre a CP.

Formate as respostas de forma clara e organizada, usando emojis quando apropriado:
🚂 para comboios
📍 para estações  
⏰ para horários
⚠️ para perturbações
💰 para preços

Exemplos de informações que pode fornecer:
- Principais linhas da CP (Alfa Pendular, Intercidades, Regional, Urbano)
- Estações principais (Lisboa Oriente, Porto Campanhã, Coimbra-B)
- Dicas sobre bilhetes e reservas
- Informações sobre acessibilidade`,
    tools: {
      getCPTrainInfo: {
        description: "Obter informações sobre comboios da CP",
        parameters: {
          type: "object",
          properties: {
            query: {
              type: "string",
              description: "Consulta sobre horários, estações, perturbações ou preços da CP",
            },
            type: {
              type: "string",
              enum: ["schedules", "disruptions", "stations", "prices"],
              description: "Tipo de informação solicitada",
            },
          },
          required: ["query", "type"],
        },
        execute: async ({ query, type }) => {
          // Simular resposta baseada no tipo de consulta
          const responses = {
            schedules: `🚂 **Horários para: ${query}**\n\nPara consultar horários exatos, recomendo:\n- Site oficial da CP: cp.pt\n- App CP: disponível na App Store e Google Play\n- Balcões das estações\n\n⏰ Principais ligações:\n- Lisboa-Porto: Alfa Pendular (2h40min)\n- Lisboa-Coimbra: Intercidades (1h30min)\n- Porto-Braga: Urbano do Porto (1h15min)`,

            disruptions: `⚠️ **Estado do serviço**\n\nPara informações atualizadas sobre perturbações:\n- Consulte cp.pt\n- Siga @CPPortugal no Twitter\n- Use a app CP\n\n📱 Dica: Ative notificações na app para alertas em tempo real sobre a sua linha habitual.`,

            stations: `📍 **Informações de estações**\n\nPrincipais estações da CP:\n🚉 **Lisboa**: Oriente, Santa Apolónia, Entrecampos\n🚉 **Porto**: Campanhã, São Bento\n🚉 **Coimbra**: Coimbra-B (principal), Coimbra-A (centro)\n\n♿ Todas as estações principais têm acessibilidade para pessoas com mobilidade reduzida.`,

            prices: `💰 **Informações de preços**\n\nTipos de bilhetes:\n🎫 **Normal**: Preço base\n🎫 **Jovem** (<26 anos): -25%\n🎫 **Sénior** (>65 anos): -25%\n🎫 **Família**: Descontos para grupos\n\n💡 **Dicas**:\n- Compre online para evitar filas\n- Cartão CP20 oferece 20% desconto\n- Bilhetes Alfa Pendular têm reserva obrigatória`,
          }

          return responses[type as keyof typeof responses] || `Informação sobre: ${query}`
        },
      },
    },
    toolChoice: "auto",
  })

  return result.toDataStreamResponse()
}
