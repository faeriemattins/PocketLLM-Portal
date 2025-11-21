import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader2, Sparkles } from 'lucide-react';
import { clsx } from 'clsx';

const ChatInterface = () => {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!input.trim() || isLoading) return;

        const userMessage = { role: 'user', content: input };
        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setIsLoading(true);

        // Prepare for streaming response
        const assistantMessage = { role: 'assistant', content: '' };
        setMessages(prev => [...prev, assistantMessage]);

        try {
            const response = await fetch('http://localhost:8000/chat/completions', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    messages: [...messages, userMessage],
                    temperature: 0.7
                })
            });

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let assistantContent = '';

            while (true) {
                const { value, done } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value);
                const lines = chunk.split('\n');

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        const dataStr = line.slice(6);
                        if (dataStr === '[DONE]') continue;

                        try {
                            const data = JSON.parse(dataStr);
                            if (data.content) {
                                assistantContent += data.content;
                                setMessages(prev => {
                                    const newMessages = [...prev];
                                    newMessages[newMessages.length - 1].content = assistantContent;
                                    return newMessages;
                                });
                            }
                        } catch (e) {
                            console.error('Error parsing JSON', e);
                        }
                    }
                }
            }
        } catch (error) {
            console.error('Error sending message:', error);
            setMessages(prev => [...prev, { role: 'system', content: 'Error: Could not connect to the server.' }]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="flex flex-col h-full relative">
            {/* Header Area */}
            <div className="absolute top-0 left-0 right-0 h-20 bg-gradient-to-b from-background/80 to-transparent z-10 pointer-events-none" />

            <div className="flex-1 overflow-y-auto p-6 space-y-6 pt-10">
                {messages.length === 0 && (
                    <div className="flex flex-col items-center justify-center h-full text-center animate-fade-in">
                        <div className="relative group">
                            <div className="absolute inset-0 bg-gradient-to-r from-primary to-accent rounded-3xl blur-xl opacity-40 group-hover:opacity-60 transition-opacity duration-500" />
                            <div className="relative w-24 h-24 rounded-3xl bg-gradient-to-br from-surface-highlight to-surface border border-white/10 flex items-center justify-center shadow-2xl mb-8 transform group-hover:scale-105 transition-transform duration-500">
                                <Sparkles className="text-primary w-12 h-12" />
                            </div>
                        </div>
                        <h3 className="text-3xl font-heading font-bold text-white mb-3 tracking-tight">How can I help you today?</h3>
                        <p className="text-gray-400 max-w-md text-lg font-light leading-relaxed">
                            I'm running locally on your CPU. Ask me anything about code, writing, or analysis.
                        </p>
                    </div>
                )}

                {messages.map((msg, idx) => (
                    <div key={idx} className={clsx(
                        "flex gap-4 max-w-[85%] animate-slide-up",
                        msg.role === 'user' ? "ml-auto flex-row-reverse" : "mr-auto"
                    )}>
                        <div className={clsx(
                            "w-10 h-10 rounded-full flex items-center justify-center shrink-0 shadow-lg border border-white/10",
                            msg.role === 'user' ? "bg-primary text-white" : "bg-surface-highlight text-accent"
                        )}>
                            {msg.role === 'user' ? <User size={20} /> : <Bot size={20} />}
                        </div>

                        <div className={clsx(
                            "p-5 rounded-2xl text-sm leading-relaxed shadow-lg backdrop-blur-md border transition-all duration-300 hover:shadow-xl",
                            msg.role === 'user'
                                ? "bg-gradient-to-br from-primary to-primary-hover text-white border-primary/20 rounded-tr-none shadow-primary/10"
                                : "bg-surface/60 text-gray-100 border-white/5 rounded-tl-none shadow-black/20"
                        )}>
                            <div className="whitespace-pre-wrap font-sans text-[15px] tracking-wide">
                                {msg.content}
                            </div>
                        </div>
                    </div>
                ))}

                {isLoading && messages[messages.length - 1]?.role === 'user' && (
                    <div className="flex gap-4 mr-auto animate-slide-up">
                        <div className="w-10 h-10 rounded-full bg-surface-highlight flex items-center justify-center shrink-0 border border-white/10">
                            <Bot size={20} className="text-accent" />
                        </div>
                        <div className="p-4 rounded-2xl bg-surface/80 border border-white/5 rounded-tl-none flex items-center gap-2">
                            <div className="w-2 h-2 bg-accent rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                            <div className="w-2 h-2 bg-accent rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                            <div className="w-2 h-2 bg-accent rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="p-6 pt-2">
                <form onSubmit={handleSubmit} className="relative max-w-4xl mx-auto">
                    <div className="absolute inset-0 bg-gradient-to-r from-primary/20 to-accent/20 rounded-2xl blur-xl opacity-50 pointer-events-none" />
                    <div className="relative flex items-center gap-2 bg-surface/80 backdrop-blur-2xl border border-white/10 rounded-2xl p-2 shadow-2xl shadow-black/50 focus-within:border-primary/50 focus-within:ring-1 focus-within:ring-primary/50 transition-all duration-300 group">
                        <input
                            type="text"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder="Type your message..."
                            className="flex-1 bg-transparent border-none focus:ring-0 text-white placeholder-gray-500 px-4 py-3 font-sans text-base"
                            disabled={isLoading}
                        />
                        <button
                            type="submit"
                            disabled={isLoading || !input.trim()}
                            className="p-3 rounded-xl bg-gradient-to-br from-primary to-primary-hover hover:to-accent disabled:opacity-50 disabled:hover:from-primary disabled:hover:to-primary-hover text-white transition-all duration-300 shadow-lg shadow-primary/20 hover:shadow-primary/40 transform hover:scale-105 active:scale-95"
                        >
                            {isLoading ? <Loader2 className="animate-spin w-5 h-5" /> : <Send className="w-5 h-5" />}
                        </button>
                    </div>
                    <p className="text-center text-xs text-gray-600 mt-3">
                        AI can make mistakes. Please verify important information.
                    </p>
                </form>
            </div>
        </div>
    );
};

export default ChatInterface;
