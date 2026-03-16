HTML_CONTENT = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>PuruAI - Server Side Mobile Editor</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
    <style>
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #374151; border-radius: 4px; }
        .blink { animation: blinker 1s linear infinite; }
        @keyframes blinker { 50% { opacity: 0.3; } }
        body { -webkit-tap-highlight-color: transparent; }
        [x-cloak] { display: none !important; }
    </style>
</head>
<body class="bg-gray-900 text-gray-100 font-sans h-[100dvh] flex flex-col overflow-hidden" x-data="puruApp()">

    <!-- Header -->
    <header class="bg-gray-800 border-b border-gray-700 p-3 flex justify-between items-center shrink-0 z-20 shadow-md">
        <div class="flex items-center gap-2">
            <div class="w-7 h-7 bg-blue-500 rounded flex items-center justify-center font-bold text-white text-sm">P</div>
            <h1 class="text-lg font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-teal-400">PuruAI</h1>
        </div>
        
        <!-- Controls & Status -->
        <div class="flex items-center gap-2 relative">
            <div class="text-[10px] sm:text-xs font-medium text-gray-400 bg-gray-900 px-3 py-1.5 rounded-full flex items-center gap-2">
                <span class="w-2 h-2 rounded-full" :class="statusColor"></span>
                <span x-text="statusText"></span>
            </div>
            
            <!-- Menu Hamburger -->
            <button x-show="screen === 'workspace'" @click="isMenuOpen = !isMenuOpen" @click.outside="isMenuOpen = false" class="p-1.5 bg-gray-700 text-gray-300 rounded-md hover:bg-gray-600 focus:outline-none transition-colors">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path></svg>
            </button>

            <!-- Dropdown Menu -->
            <div x-show="isMenuOpen" x-transition.opacity x-cloak class="absolute right-0 top-10 w-48 bg-gray-800 border border-gray-600 rounded-xl shadow-2xl z-50 overflow-hidden divide-y divide-gray-700">
                <button @click="clearSession(); isMenuOpen = false;" class="w-full text-left px-4 py-3 text-sm text-gray-200 hover:bg-gray-700 hover:text-white flex items-center gap-2 transition-colors">
                    <svg class="w-4 h-4 text-yellow-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
                    Clear Percakapan
                </button>
                <button @click="resetAll(); isMenuOpen = false;" class="w-full text-left px-4 py-3 text-sm text-red-400 hover:bg-gray-700 hover:text-red-300 flex items-center gap-2 transition-colors">
                    <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/></svg>
                    Reset All (Ke Menu Utama)
                </button>
            </div>
        </div>
    </header>

    <!-- SETUP SCREEN -->
    <div x-show="screen === 'setup'" x-transition.opacity class="flex-1 flex flex-col items-center justify-center p-6 overflow-y-auto">
        <div class="w-full max-w-sm bg-gray-800 p-6 rounded-2xl shadow-xl border border-gray-700">
            <div class="text-center mb-6">
                <h2 class="text-xl font-bold text-white mb-2">Mulai Project</h2>
                <p class="text-gray-400 text-xs">Pilih mode untuk memulai. PuruAI diproses di sisi Server.</p>
            </div>
            
            <button @click="startFreshProject()" class="w-full mb-5 bg-blue-600 active:bg-blue-700 text-white font-semibold py-3 px-4 rounded-xl transition-all flex items-center justify-center gap-2 text-sm shadow-lg shadow-blue-500/20">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg>
                Buat Project Baru
            </button>

            <div class="relative flex items-center py-2 mb-5">
                <div class="flex-grow border-t border-gray-700"></div>
                <span class="flex-shrink-0 mx-4 text-gray-500 text-xs font-medium">ATAU</span>
                <div class="flex-grow border-t border-gray-700"></div>
            </div>

            <label for="zipUpload" class="w-full cursor-pointer bg-gray-700 active:bg-gray-600 border border-dashed border-gray-500 text-white font-medium py-4 px-4 rounded-xl transition-all flex flex-col items-center justify-center gap-2">
                <svg class="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"></path></svg>
                <span class="text-sm text-gray-300">Upload ZIP Project</span>
                <span class="text-xs text-gray-500">Lanjutkan project yang sudah ada</span>
            </label>
            <input type="file" id="zipUpload" class="hidden" accept=".zip" @change="handleZipUpload($event)">
        </div>
    </div>

    <!-- WORKSPACE SCREEN -->
    <main x-show="screen === 'workspace'" x-transition.opacity class="flex-1 flex flex-col overflow-hidden relative">
        
        <!-- Tab: Chat -->
        <div x-show="activeTab === 'chat'" class="flex-1 flex flex-col overflow-hidden">
            <div id="chatContainer" class="flex-1 overflow-y-auto p-3 pb-28 space-y-3">
                <template x-for="(msg, index) in chatHistory" :key="index">
                    <div class="rounded-xl border p-3 text-sm max-w-[90%]"
                         :class="{
                            'bg-blue-900/50 border-blue-700 ml-auto': msg.role === 'user',
                            'bg-gray-800/80 border-gray-600 font-mono text-xs text-yellow-300': msg.role === 'system',
                            'bg-gray-800 border-gray-700 mr-auto': msg.role === 'ai'
                         }">
                        <div class="font-bold text-[11px] mb-1.5 uppercase tracking-wider"
                             :class="{
                                'text-blue-400': msg.role === 'user',
                                'text-yellow-500': msg.role === 'system',
                                'text-teal-400': msg.role === 'ai'
                             }" x-text="msg.role === 'user' ? 'You' : (msg.role === 'system' ? 'System Log' : 'PuruAI')">
                        </div>
                        <div class="whitespace-pre-wrap leading-relaxed break-words" x-text="msg.text"></div>
                    </div>
                </template>
                
                <div x-show="statusType === 'done'" class="pt-4 flex justify-center">
                    <a :href="'/api/download_zip/' + sessionId" class="bg-green-600 active:bg-green-700 text-white px-6 py-3 rounded-xl font-semibold text-sm transition-all shadow-lg flex items-center gap-2 animate-bounce">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg>
                        Download ZIP Sekarang
                    </a>
                </div>
            </div>

            <!-- Input Area -->
            <div class="absolute bottom-0 left-0 w-full bg-gray-900 border-t border-gray-800 p-2 sm:p-3 z-10 shadow-[0_-10px_15px_-3px_rgba(0,0,0,0.5)]">
                <div class="flex items-end gap-2">
                    
                    <!-- Tombol Upload File Konteks -->
                    <label for="contextUpload" class="cursor-pointer p-2.5 bg-gray-800 text-gray-400 hover:text-white rounded-xl border border-gray-700 transition-colors shrink-0" :class="{'opacity-50 pointer-events-none': isLooping}">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"></path></svg>
                    </label>
                    <input type="file" id="contextUpload" class="hidden" @change="handleContextUpload($event)" :disabled="isLooping">

                    <!-- Textarea Dinamis -->
                    <textarea x-model="userInput" 
                           x-ref="chatInput"
                           :disabled="isLooping"
                           placeholder="Instruksikan AI... (Enter u/ baris baru)" 
                           rows="1"
                           @input="resizeTextarea($el)"
                           class="flex-1 bg-gray-800 text-white border border-gray-700 rounded-xl px-3 py-2.5 text-sm focus:outline-none focus:border-blue-500 transition-all disabled:opacity-50 resize-none overflow-y-auto min-h-[42px] max-h-32"></textarea>
                           
                    <!-- Send Button -->
                    <button @click="sendPrompt()" :disabled="!userInput.trim() || isLooping" 
                            class="bg-blue-600 active:bg-blue-700 disabled:bg-gray-700 disabled:text-gray-500 text-white p-2.5 rounded-xl font-semibold transition-all shrink-0">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 5l7 7-7 7M5 5l7 7-7 7"></path></svg>
                    </button>
                </div>
            </div>
        </div>

        <!-- Tab: Files Explorer -->
        <div x-show="activeTab === 'files'" class="flex-1 flex flex-col bg-gray-900 overflow-hidden">
            <div class="p-3 border-b border-gray-800 bg-gray-800 text-xs font-semibold flex justify-between items-center">
                <div class="flex flex-col gap-1">
                    <span class="text-gray-400">SERVER FILE SYSTEM</span>
                    <span class="bg-gray-700 px-2 py-0.5 rounded text-gray-300 w-max">#root/</span>
                </div>
                
                <!-- TOMBOL DOWNLOAD ZIP -->
                <a :href="'/api/download_zip/' + sessionId" class="bg-blue-600 hover:bg-blue-700 text-white px-3 py-2 rounded-lg text-xs flex items-center gap-1.5 shadow-md transition-colors">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg>
                    Download ZIP
                </a>
            </div>
            
            <div class="flex-1 overflow-y-auto p-2 pb-10">
                <template x-if="filesList.length === 0">
                    <div class="text-center text-gray-600 text-sm mt-10 italic">Tidak ada file.</div>
                </template>
                <template x-for="file in filesList" :key="file">
                    <div class="flex items-center gap-3 py-2 px-3 border-b border-gray-800 text-sm text-gray-300 break-all">
                        <svg class="w-5 h-5 text-gray-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"></path></svg>
                        <span x-text="file" class="flex-1"></span>
                    </div>
                </template>
            </div>
        </div>
    </main>

    <!-- BOTTOM NAVBAR -->
    <nav x-show="screen === 'workspace'" class="bg-gray-800 border-t border-gray-700 flex justify-around items-center h-14 shrink-0 pb-safe z-30 shadow-[0_-5px_10px_rgba(0,0,0,0.2)]">
        <button @click="activeTab = 'chat'" class="flex-1 flex flex-col items-center justify-center gap-1 h-full transition-colors" :class="activeTab === 'chat' ? 'text-blue-400' : 'text-gray-500'">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path></svg>
            <span class="text-[10px] font-medium">Chat</span>
        </button>
        <button @click="activeTab = 'files'" class="flex-1 flex flex-col items-center justify-center gap-1 h-full transition-colors relative" :class="activeTab === 'files' ? 'text-blue-400' : 'text-gray-500'">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"></path></svg>
            <span class="text-[10px] font-medium">Files (<span x-text="filesList.length"></span>)</span>
        </button>
    </nav>

    <script>
        function getSessionId() {
            let sid = localStorage.getItem('puruai_session');
            if (!sid) {
                sid = 'session_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
                localStorage.setItem('puruai_session', sid);
            }
            return sid;
        }

        document.addEventListener('alpine:init', () => {
            Alpine.data('puruApp', () => ({
                sessionId: getSessionId(),
                screen: 'setup', 
                activeTab: 'chat', 
                statusText: 'Connecting...',
                statusType: 'idle', 
                isLooping: false,
                isMenuOpen: false,
                filesList: [],
                chatHistory: [],
                userInput: '',
                ws: null,

                get statusColor() {
                    const colors = {
                        idle: 'bg-gray-500',
                        active: 'bg-blue-500 blink',
                        error: 'bg-red-500 blink',
                        done: 'bg-green-500'
                    };
                    return colors[this.statusType] || 'bg-gray-500';
                },

                async init() {
                    this.$watch('chatHistory', () => {
                        this.$nextTick(() => {
                            const chatEl = document.getElementById('chatContainer');
                            if (chatEl) chatEl.scrollTop = chatEl.scrollHeight;
                        });
                    });
                    
                    if(localStorage.getItem('puruai_started') === 'true') {
                        try {
                            const res = await fetch('/api/check_session/' + this.sessionId);
                            const data = await res.json();
                            if(!data.valid) {
                                alert("Sesi lama Anda telah kadaluarsa (3 hari) dan dihapus otomatis oleh Server. Silakan mulai project baru.");
                                this.screen = 'setup';
                                localStorage.removeItem('puruai_started');
                                return;
                            }
                        } catch(e) {
                            console.error("Gagal cek session", e);
                        }
                        
                        this.screen = 'workspace';
                        this.connectWS();
                    }
                },

                connectWS() {
                    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                    this.ws = new WebSocket(`${protocol}//${window.location.host}/ws/${this.sessionId}`);
                    
                    this.ws.onopen = () => {
                        this.statusText = 'Connected Server';
                        this.statusType = 'idle';
                    };
                    
                    this.ws.onmessage = (event) => {
                        const msg = JSON.parse(event.data);
                        if (msg.type === 'chat_update') {
                            this.chatHistory = msg.data;
                        } else if (msg.type === 'vfs') {
                            this.filesList = msg.data;
                        } else if (msg.type === 'status') {
                            this.statusText = msg.text;
                            this.statusType = msg.statusType;
                            if(msg.isLooping !== undefined) this.isLooping = msg.isLooping;
                        } else if (msg.type === 'loop_state') {
                            this.isLooping = msg.isLooping;
                        }
                    };

                    this.ws.onclose = () => {
                        this.statusText = 'Disconnected. Reconnecting...';
                        this.statusType = 'error';
                        setTimeout(() => this.connectWS(), 3000);
                    };
                },

                resizeTextarea(el) {
                    el.style.height = 'auto';
                    let newHeight = el.scrollHeight;
                    if(newHeight > 128) newHeight = 128; 
                    el.style.height = newHeight + 'px';
                },

                startFreshProject() {
                    this.screen = 'workspace';
                    localStorage.setItem('puruai_started', 'true');
                    this.clearSession(); 
                    if(!this.ws || this.ws.readyState !== 1) {
                        this.connectWS();
                    }
                },

                async clearSession() {
                    const formData = new FormData();
                    formData.append('session_id', this.sessionId);
                    await fetch('/api/clear_session', { method: 'POST', body: formData });
                    this.chatHistory = [];
                    this.isLooping = false;
                    this.statusType = 'idle';
                    this.statusText = 'Idle';
                    this.activeTab = 'chat';
                },
                
                async resetAll() {
                    const formData = new FormData();
                    formData.append('session_id', this.sessionId);
                    await fetch('/api/delete_session', { method: 'POST', body: formData });
                    
                    localStorage.removeItem('puruai_started');
                    localStorage.removeItem('puruai_session'); 
                    
                    if(this.ws) this.ws.close();
                    
                    this.sessionId = getSessionId(); 
                    this.chatHistory = [];
                    this.filesList = [];
                    this.screen = 'setup';
                },

                async handleZipUpload(event) {
                    const file = event.target.files[0];
                    if (!file) return;

                    this.statusText = 'Uploading & Extracting...';
                    this.statusType = 'active';
                    
                    const formData = new FormData();
                    formData.append('session_id', this.sessionId);
                    formData.append('file', file);

                    try {
                        const res = await fetch('/api/upload_zip', { method: 'POST', body: formData });
                        if(res.ok) {
                            this.screen = 'workspace';
                            localStorage.setItem('puruai_started', 'true');
                            this.statusText = 'Idle';
                            this.statusType = 'idle';
                            if(!this.ws || this.ws.readyState !== 1) this.connectWS();
                        } else {
                            alert("Gagal mengupload ZIP.");
                        }
                    } catch (err) {
                        alert("Error: " + err.message);
                    }
                    event.target.value = '';
                },

                async handleContextUpload(event) {
                    const file = event.target.files[0];
                    if (!file || this.isLooping) return;

                    const formData = new FormData();
                    formData.append('session_id', this.sessionId);
                    formData.append('file', file);

                    try {
                        this.statusText = 'Uploading Konteks...';
                        this.statusType = 'active';

                        const res = await fetch('/api/upload_context', { method: 'POST', body: formData });
                        if(!res.ok) alert("Gagal mengupload file konteks.");
                        
                        this.statusText = 'Idle';
                        this.statusType = 'idle';
                    } catch (err) {
                        alert("Error: " + err.message);
                    }
                    event.target.value = '';
                },

                sendPrompt() {
                    const val = this.userInput.trim();
                    if (!val || this.isLooping) return;
                    
                    this.isLooping = true;
                    this.userInput = '';
                    
                    this.$refs.chatInput.style.height = 'auto';
                    
                    if(this.statusType === 'done') {
                        this.statusType = 'idle';
                        this.statusText = 'Berpikir...';
                    }
                    
                    this.ws.send(JSON.stringify({ action: 'prompt', text: val }));
                }
            }));
        });
    </script>
</body>
</html>
"""
