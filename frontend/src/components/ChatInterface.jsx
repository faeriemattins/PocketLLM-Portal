import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader2, Sparkles, Plus, MessageSquare, Trash2, AlertTriangle } from 'lucide-react';
import { clsx } from 'clsx';
import { getSessions, createSession, deleteSession, getSessionMessages, generateSessionTitle } from '../api';

const ChatInterface = () => {
    const [sessions, setSessions] = useState([]);
    const [currentSessionId, setCurrentSessionId] = useState(null);
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [deleteConfirm, setDeleteConfirm] = useState(null);
    const [sessionLimitReached, setSessionLimitReached] = useState(false);
    const [limitErrorMessage, setLimitErrorMessage] = useState('');
    const messagesContainerRef = useRef(null);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        if (messagesContainerRef.current) {
            messagesContainerRef.current.scrollTop = messagesContainerRef.current.scrollHeight;
        }
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    // Fetch sessions on mount
    useEffect(() => {
        loadSessions();
    }, []);

    const loadSessions = async () => {
        try {
            const data = await getSessions();
            setSessions(data);
            if (data.length > 0 && !currentSessionId) {
                selectSession(data[0].id);
            }
        } catch (error) {
            console.error("Failed to load sessions", error);
        }
    };

    const selectSession = async (sessionId) => {
        setCurrentSessionId(sessionId);
        setSessionLimitReached(false);
        setLimitErrorMessage('');
        try {
            const msgs = await getSessionMessages(sessionId);
            setMessages(msgs);
        } catch (error) {
            console.error("Failed to load messages", error);
        }
    };

    const handleNewChat = async () => {
        try {
            const newSession = await createSession();
            setSessions([newSession, ...sessions]);
            setCurrentSessionId(newSession.id);
            setMessages([]);
            setSessionLimitReached(false);
            setLimitErrorMessage('');
        } catch (error) {
            console.error("Failed to create session", error);
        }
    };

    const handleDeleteSession = (e, sessionId) => {
        e.preventDefault();
        e.stopPropagation();
        setDeleteConfirm(sessionId);
    };

    const confirmDelete = async () => {
        if (!deleteConfirm) return;
        try {
            await deleteSession(deleteConfirm);
            const updatedSessions = sessions.filter(s => s.id !== deleteConfirm);
            setSessions(updatedSessions);
            if (currentSessionId === deleteConfirm) {
                if (updatedSessions.length > 0) {
                    selectSession(updatedSessions[0].id);
                } else {
                    setCurrentSessionId(null);
                    setMessages([]);
                    setSessionLimitReached(false);
                    setLimitErrorMessage('');
                }
            }
        } catch (error) {
            console.error("Failed to delete session", error);
        } finally {
            setDeleteConfirm(null);
        }
    };

    const cancelDelete = () => {
        setDeleteConfirm(null);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!input.trim() || isLoading || sessionLimitReached) return;

        let activeSessionId = currentSessionId;
        const isFirstMessage = messages.length === 0;
        const currentInput = input; // Capture input for title generation

        if (!activeSessionId) {
            try {
                const newSession = await createSession(input.slice(0, 30) + "...");
                setSessions([newSession, ...sessions]);
                activeSessionId = newSession.id;
                setCurrentSessionId(activeSessionId);
            } catch (error) {
                console.error("Failed to create session", error);
                return;
            }
        }

        const userMessage = { role: 'user', content: input };
        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setIsLoading(true);

        // Prepare for streaming response
        const assistantMessage = { role: 'assistant', content: '' };
        setMessages(prev => [...prev, assistantMessage]);

        try {
            const token = localStorage.getItem('pocketllm_token');
            const response = await fetch('http://127.0.0.1:8000/chat/completions', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...(token ? { 'Authorization': `Bearer ${token}` } : {})
                },
                body: JSON.stringify({
                    messages: [...messages, userMessage],
                    temperature: 0.7,
                    session_id: activeSessionId
                })
            });

            if (!response.ok) {
                console.log("DEBUG: Response not OK. Status:", response.status);
                const errorData = await response.json().catch(() => ({}));
                console.log("DEBUG: Error data:", errorData);

                // Check for session limit error (400 Bad Request with specific message)
                if (response.status === 400 && errorData.detail && errorData.detail.includes('maximum')) {
                    console.log("DEBUG: Session limit reached! Setting state.");
                    setSessionLimitReached(true);
                    setLimitErrorMessage(errorData.detail);
                    // Remove the empty assistant message
                    setMessages(prev => prev.slice(0, -1));
                    setIsLoading(false);
                    return;
                }

                if (response.status === 403) {
                    throw new Error(errorData.detail || "Limit has exceeded, open a new chat");
                }
                throw new Error("Failed to fetch response");
            }

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

            // Generate title if it was the first message
            if (isFirstMessage) {
                console.log("Attempting to generate title for session:", activeSessionId);
                try {
                    const updatedSession = await generateSessionTitle(activeSessionId, currentInput);
                    console.log("Title generated successfully:", updatedSession);
                    setSessions(prev => prev.map(s => s.id === activeSessionId ? { ...s, title: updatedSession.title } : s));
                } catch (error) {
                    console.error("Failed to generate title", error);
                }
            }

        } catch (error) {
            console.error('Error sending message:', error);
            const errorMessage = error.message || 'Error: Could not connect to the server.';
            setMessages(prev => [...prev, { role: 'system', content: errorMessage }]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="flex h-full">
            {/* Session Sidebar */}
            <div className="w-64 bg-black/20 border-r border-white/5 flex flex-col">
                <div className="p-4 border-b border-white/5">
                    <button
                        onClick={handleNewChat}
                        type="button"
                        className="w-full flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white py-3 px-4 rounded-xl transition-all duration-300 shadow-lg shadow-indigo-500/20 font-medium"
                    >
                        <Plus size={18} />
                        <span>New Chat</span>
                    </button>
                </div>
                <div className="flex-1 overflow-y-auto px-2 space-y-1">
                    {sessions.map(session => (
                        <div
                            key={session.id}
                            className={clsx(
                                "group flex items-center justify-between rounded-lg transition-all duration-200",
                                currentSessionId === session.id
                                    ? "bg-white/10 text-white"
                                    : "text-gray-400 hover:bg-white/5 hover:text-gray-200"
                            )}
                        >
                            <div
                                onClick={() => selectSession(session.id)}
                                className="flex items-center gap-3 overflow-hidden p-3 flex-1 cursor-pointer"
                            >
                                <MessageSquare size={16} className="shrink-0" />
                                <span className="truncate text-sm font-medium">{session.title}</span>
                            </div>
                            <button
                                type="button"
                                onClick={(e) => handleDeleteSession(e, session.id)}
                                className="p-2 mr-2 text-gray-500 hover:bg-red-500/10 hover:text-red-400 rounded-lg transition-all z-10 shrink-0"
                                title="Delete Chat"
                            >
                                <Trash2 size={16} />
                            </button>
                        </div>
                    ))}
                </div>
            </div>

            {/* Chat Area */}
            <div className="flex-1 flex flex-col h-full relative">
                {/* Header Area */}
                <div className="absolute top-0 left-0 right-0 h-20 bg-gradient-to-b from-background/80 to-transparent z-10 pointer-events-none" />

                <div ref={messagesContainerRef} className="flex-1 overflow-y-auto p-6 space-y-6 pt-10">
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
                                Ask me anything about code, writing, or analysis.
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

                {/* Session Limit Warning Banner */}
                {sessionLimitReached && (
                    <div className="px-6 py-4 bg-amber-500/10 border-t border-amber-500/20 backdrop-blur-md animate-fade-in">
                        <div className="flex items-center justify-between max-w-4xl mx-auto gap-4">
                            <div className="flex items-center gap-3 text-amber-400">
                                <div className="p-2 rounded-full bg-amber-500/20 shrink-0">
                                    <AlertTriangle size={20} />
                                </div>
                                <div>
                                    <p className="font-medium text-sm">Session Limit Reached</p>
                                    <p className="text-xs text-amber-400/80">{limitErrorMessage}</p>
                                </div>
                            </div>
                            <button
                                onClick={handleNewChat}
                                className="px-4 py-2 bg-amber-500 hover:bg-amber-600 text-black font-medium text-sm rounded-lg transition-all shadow-lg shadow-amber-500/20 hover:shadow-amber-500/40 whitespace-nowrap"
                            >
                                Start New Chat
                            </button>
                        </div>
                    </div>
                )}

                {/* Input Area */}
                <div className="p-6 pt-2">
                    <form onSubmit={handleSubmit} className="relative max-w-4xl mx-auto">
                        <div className="absolute inset-0 bg-gradient-to-r from-primary/20 to-accent/20 rounded-2xl blur-xl opacity-50 pointer-events-none" />
                        <div className={clsx(
                            "relative flex items-center gap-2 bg-surface/80 backdrop-blur-2xl border border-white/10 rounded-2xl p-2 shadow-2xl shadow-black/50 transition-all duration-300 group",
                            sessionLimitReached ? "opacity-50 grayscale" : "focus-within:border-primary/50 focus-within:ring-1 focus-within:ring-primary/50"
                        )}>
                            <input
                                type="text"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                placeholder={sessionLimitReached ? "Session limit reached. Please start a new chat." : "Type your message..."}
                                className={clsx(
                                    "flex-1 bg-transparent border-none focus:ring-0 text-white placeholder-gray-500 px-4 py-3 font-sans text-base",
                                    sessionLimitReached && "cursor-not-allowed"
                                )}
                                disabled={isLoading || sessionLimitReached}
                            />
                            <button
                                type="submit"
                                disabled={isLoading || !input.trim() || sessionLimitReached}
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

            {/* Delete Confirmation Modal */}
            {deleteConfirm && (
                <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
                    <div className="bg-surface border border-white/10 rounded-2xl p-6 max-w-md mx-4 shadow-2xl animate-fade-in">
                        <h3 className="text-xl font-semibold text-white mb-2">Delete Chat?</h3>
                        <p className="text-gray-400 mb-6">
                            Are you sure you want to delete this chat? This action cannot be undone.
                        </p>
                        <div className="flex gap-3 justify-end">
                            <button
                                onClick={cancelDelete}
                                className="px-4 py-2 rounded-lg bg-white/5 hover:bg-white/10 text-gray-300 transition-all"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={confirmDelete}
                                className="px-4 py-2 rounded-lg bg-red-500 hover:bg-red-600 text-white transition-all"
                            >
                                Delete
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default ChatInterface;
