import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from openai import OpenAI
from scrapping import getProximosJogos, getResultadosRecentes

load_dotenv()

openaiApiKey = os.getenv("GPT_KEY")
telegramKey = os.getenv("TELEGRAM_KEY")
urlFuria = 'https://www.hltv.org/team/8297/furia'

client = OpenAI(api_key=openaiApiKey)

async def handleMessage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    userMessage = update.message.text

    prompt = f"""
    Você é um assistente simpático e entusiasta da FURIA, especializado em CS2.
    Quando um usuário perguntar sobre jogos ou resultados, você precisa determinar qual função deve ser executada:

    - Para resultados passados: use a função getResultadosRecentes()
    - Para próximos jogos: use a função getProximosJogos()

    Sua resposta deve ser uma string simples, indicando qual função chamar!

    O usuário perguntou: "{userMessage}"
    """

    response = client.responses.create(
        model="gpt-4o", 
        input=prompt
    )

    responseText = response.output_text.strip()

    if 'getproximosjogos' in responseText.lower():
        result = getProximosJogos(f'{urlFuria}#tab-matchesBox')
        responseMessage = "Aqui estão os próximos jogos da FURIA, preparados especialmente para você! 🎮🔥"
    elif 'getresultadosrecentes' in responseText.lower():
        results = getResultadosRecentes(f'{urlFuria}#tab-matchesBox')
        formattedResults = []
        recentResults = results[:5]

        for result in recentResults:
            if isinstance(result, tuple) and len(result) == 6:
                dataStr, time1, score1, time2, score2, tournament = result

                if "FURIA" in time1:
                    outcome = "VITÓRIA 🏆" if int(score1) > int(score2) else "DERROTA 😞"
                    formattedResults.append(f"{dataStr} - {time1} ({score1}) vs {time2} ({score2}) - {outcome} - {tournament}")
                elif "FURIA" in time2:
                    outcome = "VITÓRIA 🏆" if int(score2) > int(score1) else "DERROTA 😞"
                    formattedResults.append(f"{dataStr} - {time1} ({score1}) vs {time2} ({score2}) - {outcome} - {tournament}")

        responseMessage = "Aqui estão as **últimas 5 partidas** da FURIA! ⚡️🔥"
        result = formattedResults if formattedResults else ["Parece que não encontramos resultados recentes da FURIA, mas não se preocupe, logo logo terá mais! ✨"]
    else:
        result = ["Desculpe, não entendi a sua solicitação. Mas não se preocupe, estou aqui para ajudar! 😅"]
        responseMessage = "Parece que não entendi bem, mas vou tentar de novo! 😉"

    await update.message.reply_text(f"{responseMessage}\n\n" + "\n".join(result))

if __name__ == '__main__':
    app = ApplicationBuilder().token(telegramKey).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handleMessage))
    app.run_polling()
