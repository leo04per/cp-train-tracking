"use client"

import type React from "react"

import { useChat } from "ai/react"
import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Train, Clock, MapPin, AlertCircle } from "lucide-react"

export default function CPTracker() {
  const { messages, input, handleInputChange, handleSubmit, isLoading } = useChat()
  const [isTyping, setIsTyping] = useState(false)

  const onSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    setIsTyping(true)
    handleSubmit(e).finally(() => setIsTyping(false))
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-green-50">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="flex items-center justify-center gap-3 mb-4">
              <div className="p-3 bg-blue-600 rounded-full">
                <Train className="h-8 w-8 text-white" />
              </div>
              <h1 className="text-4xl font-bold text-gray-800">CP Tracker</h1>
            </div>
            <p className="text-gray-600 text-lg">Assistente inteligente para informações sobre comboios da CP</p>
            <div className="flex items-center justify-center gap-4 mt-4">
              <Badge variant="secondary" className="flex items-center gap-1">
                <Clock className="h-3 w-3" />
                Horários em tempo real
              </Badge>
              <Badge variant="secondary" className="flex items-center gap-1">
                <MapPin className="h-3 w-3" />
                Todas as estações
              </Badge>
              <Badge variant="secondary" className="flex items-center gap-1">
                <AlertCircle className="h-3 w-3" />
                Alertas de serviço
              </Badge>
            </div>
          </div>

          {/* Chat Interface */}
          <Card className="shadow-xl border-0">
            <CardHeader className="bg-gradient-to-r from-blue-600 to-green-600 text-white rounded-t-lg">
              <CardTitle className="flex items-center gap-2">
                <Train className="h-5 w-5" />
                Chat CP Tracker
              </CardTitle>
            </CardHeader>

            <CardContent className="h-[60vh] overflow-y-auto p-6 bg-white">
              {messages.length === 0 && (
                <div className="text-center text-gray-500 mt-8">
                  <Train className="h-16 w-16 mx-auto mb-4 text-gray-300" />
                  <h3 className="text-lg font-semibold mb-2">Bem-vindo ao CP Tracker!</h3>
                  <p className="mb-4">Pergunte-me sobre:</p>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-w-md mx-auto">
                    <div className="p-3 bg-blue-50 rounded-lg text-sm">🚂 Horários de comboios</div>
                    <div className="p-3 bg-green-50 rounded-lg text-sm">📍 Informações de estações</div>
                    <div className="p-3 bg-yellow-50 rounded-lg text-sm">⚠️ Perturbações no serviço</div>
                    <div className="p-3 bg-purple-50 rounded-lg text-sm">🎫 Preços e bilhetes</div>
                  </div>
                </div>
              )}

              {messages.map((m) => (
                <div key={m.id} className={`mb-6 ${m.role === "user" ? "text-right" : "text-left"}`}>
                  <div
                    className={`inline-block max-w-[80%] p-4 rounded-2xl ${
                      m.role === "user"
                        ? "bg-blue-600 text-white rounded-br-md"
                        : "bg-gray-100 text-gray-800 rounded-bl-md"
                    }`}
                  >
                    <div className="whitespace-pre-wrap">{m.content}</div>
                  </div>
                  <div className={`text-xs text-gray-500 mt-1 ${m.role === "user" ? "text-right" : "text-left"}`}>
                    {m.role === "user" ? "Você" : "CP Tracker"}
                  </div>
                </div>
              ))}

              {(isLoading || isTyping) && (
                <div className="text-left mb-6">
                  <div className="inline-block p-4 rounded-2xl bg-gray-100 text-gray-800 rounded-bl-md">
                    <div className="flex items-center gap-2">
                      <div className="flex gap-1">
                        <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce"></div>
                        <div
                          className="w-2 h-2 bg-blue-600 rounded-full animate-bounce"
                          style={{ animationDelay: "0.1s" }}
                        ></div>
                        <div
                          className="w-2 h-2 bg-blue-600 rounded-full animate-bounce"
                          style={{ animationDelay: "0.2s" }}
                        ></div>
                      </div>
                      <span className="text-sm">CP Tracker está a processar...</span>
                    </div>
                  </div>
                </div>
              )}
            </CardContent>

            <CardFooter className="bg-gray-50 rounded-b-lg p-6">
              <form onSubmit={onSubmit} className="flex w-full gap-3">
                <Input
                  value={input}
                  onChange={handleInputChange}
                  placeholder="Pergunte sobre horários, estações, perturbações..."
                  className="flex-grow border-gray-300 focus:border-blue-500 focus:ring-blue-500"
                  disabled={isLoading}
                />
                <Button
                  type="submit"
                  disabled={isLoading || !input.trim()}
                  className="bg-blue-600 hover:bg-blue-700 px-6"
                >
                  {isLoading ? (
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  ) : (
                    "Enviar"
                  )}
                </Button>
              </form>
              <div className="text-xs text-gray-500 mt-2 text-center w-full">
                Conectado ao sistema MCP da CP para informações em tempo real
              </div>
            </CardFooter>
          </Card>

          {/* Quick Actions */}
          <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-3">
            <Button
              variant="outline"
              className="h-auto p-4 flex flex-col items-center gap-2"
              onClick={() => handleInputChange({ target: { value: "Horários Lisboa-Porto hoje" } } as any)}
            >
              <Clock className="h-5 w-5 text-blue-600" />
              <span className="text-sm">Horários</span>
            </Button>
            <Button
              variant="outline"
              className="h-auto p-4 flex flex-col items-center gap-2"
              onClick={() => handleInputChange({ target: { value: "Perturbações no serviço hoje" } } as any)}
            >
              <AlertCircle className="h-5 w-5 text-red-600" />
              <span className="text-sm">Perturbações</span>
            </Button>
            <Button
              variant="outline"
              className="h-auto p-4 flex flex-col items-center gap-2"
              onClick={() => handleInputChange({ target: { value: "Estações próximas de Lisboa" } } as any)}
            >
              <MapPin className="h-5 w-5 text-green-600" />
              <span className="text-sm">Estações</span>
            </Button>
            <Button
              variant="outline"
              className="h-auto p-4 flex flex-col items-center gap-2"
              onClick={() => handleInputChange({ target: { value: "Preços bilhetes Lisboa-Coimbra" } } as any)}
            >
              <Train className="h-5 w-5 text-purple-600" />
              <span className="text-sm">Preços</span>
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}
