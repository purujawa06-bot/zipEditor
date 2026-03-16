HTML_CONTENT = r"""
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

        .xml-todo-card {
            background: linear-gradient(135deg, rgba(13,148,136,0.08), rgba(6,95,70,0.12));
            border: 1px solid rgba(45,212,191,0.25);
            border-radius: 12px;
            overflow: hidden;
            margin: 8px 0;
        }
        .xml-todo-header {
            background: rgba(13,148,136,0.15);
            border-bottom: 1px solid rgba(45,212,191,0.2);
            padding: 7px 12px;
            display: flex;
            align-items: center;
            gap: 7px;
        }
        .xml-exec-card {
            background: linear-gradient(135deg, rgba(30,58,138,0.15), rgba(17,24,39,0.5));
            border: 1px solid rgba(59,130,246,0.25);
            border-radius: 12px;
            overflow: hidden;
            margin: 8px 0;
        }
        .xml-exec-header {
            background: rgba(30,64,175,0.2);
            border-bottom: 1px solid rgba(59,130,246,0.2);
            padding: 7px 12px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 7px;
        }
        .exec-pre {
            padding: 10px 12px;
            font-size: 11px;
            font-family: 'Courier New', monospace;
            color: rgba(134,239,172,0.9);
            white-space: pre-wrap;
            word-break: break-all;
            line-height: 1.6;
            margin: 0;
        }
        .todo-step {
            display: flex;
            align-items: flex-start;
            gap: 10px;
            padding: 4px 0;
        }
        .todo-badge {
            width: 20px;
            height: 20px;
            background: rgba(13,148,136,0.3);
            border: 1px solid rgba(45,212,191,0.4);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 10px;
            font-weight: 700;
            color: #5eead4;
            flex-shrink: 0;
            margin-top: 2px;
        }
        .read-more-btn {
            font-size: 11px;
            color: #60a5fa;
            background: rgba(30,64,175,0.2);
            border: 1px solid rgba(59,130,246,0.3);
            border-radius: 6px;
            padding: 2px 8px;
            cursor: pointer;
            transition: all 0.15s;
            white-space: nowrap;
        }
        .read-more-btn:hover { background: rgba(30,64,175,0.4); }
        .cmd-badge {
            font-family: monospace;
            font-size: 10px;
            font-weight: 700;
            padding: 2px 7px;
            border-radius: 5px;
            background: rgba(0,0,0,0.3);
        }
    </style>
</head>
<body class="bg-gray-900 text-gray-100 font-sans h-[100dvh] flex flex-col overflow-hidden" x-data="puruApp()">

    <!-- Header -->
    <header class="bg-gray-800 border-b border-gray-700 p-3 flex justify-between items-center shrink-0 z-20 shadow-md">
        <div class="flex items-center gap-2">
            <div class="w-7 h-7 bg-blue-500 rounded flex items-center justify-center font-bold text-white text-sm">P</div>
            <h1 class="text-lg font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-teal-400">PuruAI</h1>
        </div>
        <div class="flex items-center gap-2 relative">
            <div class="text-[10px] sm:text-xs font-medium text-gray-400 bg-gray-900 px-3 py-1.5 rounded-full flex items-center gap-2">
                <span class="w-2 h-2 rounded-full" :class="statusColor"></span>
                <span x-text="statusText"></span>
            </div>
            <button x-show="screen === 'workspace'" @click="isMenuOpen = !isMenuOpen" @click.outside="isMenuOpen = false" class="p-1.5 bg-gray-700 text-gray-300 rounded-md hover:bg-gray-600 focus:outline-none transition-colors">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path></svg>
            </button>
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
                    <div class="rounded-xl border p-3 text-sm"
                         :class="{
                            'bg-blue-900/50 border-blue-700 ml-auto max-w-[90%]': msg.role === 'user',
                            'bg-gray-800/80 border-gray-700/60 w-full': msg.role === 'system',
                            'bg-gray-800 border-gray-700 mr-auto max-w-[95%]': msg.role === 'ai'
                         }">
                        <div class="font-bold text-[11px] mb-2 uppercase tracking-wider flex items-center gap-1.5"
                             :class="{
                                'text-blue-400': msg.role === 'user',
                                'text-yellow-500': msg.role === 'system',
                                'text-teal-400': msg.role === 'ai'
                             }">
                            <template x-if="msg.role === 'user'">
                                <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 24 24"><path d="M12 12c2.7 0 4.8-2.1 4.8-4.8S14.7 2.4 12 2.4 7.2 4.5 7.2 7.2 9.3 12 12 12zm0 2.4c-3.2 0-9.6 1.6-9.6 4.8v2.4h19.2v-2.4c0-3.2-6.4-4.8-9.6-4.8z"/></svg>
                            </template>
                            <template x-if="msg.role === 'system'">
                                <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3H5a2 2 0 00-2 2v4m6-6h10a2 2 0 012 2v4M9 3v18m0 0h10a2 2 0 002-2V9M9 21H5a2 2 0 01-2-2V9m0 0h18"/></svg>
                            </template>
                            <template x-if="msg.role === 'ai'">
                                <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/></svg>
                            </template>
                            <span x-text="msg.role === 'user' ? 'You' : (msg.role === 'system' ? 'System Log' : 'PuruAI')"></span>
                        </div>
                        <div class="leading-relaxed break-words"
                             :class="msg.role === 'system' ? 'font-mono text-xs' : 'text-sm'"
                             x-html="renderMessage(msg.text, msg.role)"></div>
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
                    <label for="contextUpload" class="cursor-pointer p-2.5 bg-gray-800 text-gray-400 hover:text-white rounded-xl border border-gray-700 transition-colors shrink-0" :class="{'opacity-50 pointer-events-none': isLooping}">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"></path></svg>
                    </label>
                    <input type="file" id="contextUpload" class="hidden" @change="handleContextUpload($event)" :disabled="isLooping">
                    <textarea x-model="userInput"
                           x-ref="chatInput"
                           :disabled="isLooping"
                           placeholder="Instruksikan AI... (Enter u/ baris baru)"
                           rows="1"
                           @input="resizeTextarea($el)"
                           class="flex-1 bg-gray-800 text-white border border-gray-700 rounded-xl px-3 py-2.5 text-sm focus:outline-none focus:border-blue-500 transition-all disabled:opacity-50 resize-none overflow-y-auto min-h-[42px] max-h-32"></textarea>
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
        // ============================================================
        // XML TAG RENDERER
        // ============================================================
        const _expandState = {};

        window.toggleExpand = function(uid) {
            const shortEl = document.getElementById('exec-short-' + uid);
            const fullEl  = document.getElementById('exec-full-' + uid);
            const btn     = document.getElementById('btn-expand-' + uid);
            if (!shortEl || !fullEl || !btn) return;
            _expandState[uid] = !_expandState[uid];
            if (_expandState[uid]) {
                shortEl.style.display = 'none';
                fullEl.style.display  = 'block';
                btn.textContent = 'Sembunyikan \u2191';
            } else {
                shortEl.style.display = 'block';
                fullEl.style.display  = 'none';
                btn.textContent = 'Baca Selengkapnya \u2193';
            }
        };

        function escHtml(s) {
            return String(s)
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;')
                .replace(/"/g, '&quot;');
        }

        function renderTodoBlock(inner) {
            const itemRe = /<index_(\d+)>([\s\S]*?)<\/index_\d+>/gi;
            const items  = [];
            let im;
            while ((im = itemRe.exec(inner)) !== null) {
                items.push({ num: parseInt(im[1]), text: im[2].trim() });
            }
            items.sort((a, b) => a.num - b.num);

            const stepsHtml = items.length > 0
                ? items.map(i =>
                    '<div class="todo-step">' +
                        '<div class="todo-badge">' + i.num + '</div>' +
                        '<span style="color:#e2e8f0;font-size:13px;line-height:1.6;">' + escHtml(i.text) + '</span>' +
                    '</div>'
                  ).join('')
                : '<div style="color:#94a3b8;font-size:12px;padding:4px 0;">' + escHtml(inner.trim()) + '</div>';

            return '<div class="xml-todo-card">' +
                '<div class="xml-todo-header">' +
                    '<svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="#2dd4bf" stroke-width="2">' +
                        '<path stroke-linecap="round" stroke-linejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"/>' +
                    '</svg>' +
                    '<span style="color:#5eead4;font-size:11px;font-weight:700;letter-spacing:.07em;text-transform:uppercase;">Rencana Todo</span>' +
                    '<span style="color:#0d9488;font-size:10px;margin-left:auto;">' + items.length + ' langkah</span>' +
                '</div>' +
                '<div style="padding:10px 12px;display:flex;flex-direction:column;gap:6px;">' + stepsHtml + '</div>' +
            '</div>';
        }

        function renderExecutionBlock(inner) {
            const uid     = Math.random().toString(36).substr(2, 7);
            const trimmed = inner.trim();
            const cmdName = (trimmed.split(/[\s<\n]/)[0] || trimmed).toLowerCase();

            const cmdMeta = {
                'write':  { color: '#93c5fd', bg: 'rgba(30,64,175,0.3)'   },
                'read':   { color: '#fde68a', bg: 'rgba(120,83,19,0.3)'   },
                'all':    { color: '#d1d5db', bg: 'rgba(75,85,99,0.3)'    },
                'remove': { color: '#fca5a5', bg: 'rgba(127,29,29,0.3)'   },
                'move':   { color: '#c4b5fd', bg: 'rgba(91,33,182,0.3)'   },
                'curl':   { color: '#fdba74', bg: 'rgba(124,45,18,0.3)'   },
                'stop':   { color: '#f87171', bg: 'rgba(153,27,27,0.4)'   },
                'todo':   { color: '#5eead4', bg: 'rgba(13,148,136,0.3)'  },
            };
            const meta    = cmdMeta[cmdName] || { color: '#86efac', bg: 'rgba(20,83,45,0.3)' };
            const isLong  = trimmed.length > 220;
            const preview = isLong ? trimmed.slice(0, 220) : trimmed;

            const btnHtml  = isLong
                ? '<button id="btn-expand-' + uid + '" class="read-more-btn" onclick="toggleExpand(\'' + uid + '\')">Baca Selengkapnya \u2193</button>'
                : '';
            const fullPre  = isLong
                ? '<pre id="exec-full-' + uid + '" class="exec-pre" style="display:none;">' + escHtml(trimmed) + '</pre>'
                : '';

            return '<div class="xml-exec-card">' +
                '<div class="xml-exec-header">' +
                    '<div style="display:flex;align-items:center;gap:7px;">' +
                        '<svg width="13" height="13" fill="none" viewBox="0 0 24 24" stroke="#60a5fa" stroke-width="2">' +
                            '<path stroke-linecap="round" stroke-linejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z"/>' +
                        '</svg>' +
                        '<span style="color:#93c5fd;font-size:11px;font-weight:700;letter-spacing:.07em;text-transform:uppercase;">execution</span>' +
                        '<span class="cmd-badge" style="color:' + meta.color + ';background:' + meta.bg + ';">' + escHtml(cmdName) + '</span>' +
                    '</div>' +
                    btnHtml +
                '</div>' +
                '<pre id="exec-short-' + uid + '" class="exec-pre">' + escHtml(preview) +
                    (isLong ? '<span style="color:#4b5563;">...</span>' : '') +
                '</pre>' +
                fullPre +
            '</div>';
        }

        function renderMessage(text, role) {
            if (!text) return '';
            if (role === 'user') {
                return '<span style="white-space:pre-wrap;">' + escHtml(text) + '</span>';
            }

            const segments = [];
            const tagRe    = /<(todo|execution)>([\s\S]*?)<\/(todo|execution)>/gi;
            let cursor     = 0, m;

            while ((m = tagRe.exec(text)) !== null) {
                if (m.index > cursor) {
                    segments.push({ type: 'text', content: text.slice(cursor, m.index) });
                }
                segments.push({ type: m[1].toLowerCase(), inner: m[2] });
                cursor = m.index + m[0].length;
            }
            if (cursor < text.length) {
                segments.push({ type: 'text', content: text.slice(cursor) });
            }
            if (segments.length === 0) {
                segments.push({ type: 'text', content: text });
            }

            let html = '';
            for (const seg of segments) {
                if (seg.type === 'text') {
                    const t = seg.content.trim();
                    if (t) html += '<span style="white-space:pre-wrap;word-break:break-word;">' + escHtml(t) + '</span>';
                } else if (seg.type === 'todo') {
                    html += renderTodoBlock(seg.inner);
                } else if (seg.type === 'execution') {
                    html += renderExecutionBlock(seg.inner);
                }
            }
            return html || '<span style="white-space:pre-wrap;">' + escHtml(text) + '</span>';
        }

        // ============================================================
        // ALPINE APP
        // ============================================================
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
                    const c = { idle:'bg-gray-500', active:'bg-blue-500 blink', error:'bg-red-500 blink', done:'bg-green-500' };
                    return c[this.statusType] || 'bg-gray-500';
                },

                renderMessage(text, role) { return renderMessage(text, role); },

                async init() {
                    this.$watch('chatHistory', () => {
                        this.$nextTick(() => {
                            const el = document.getElementById('chatContainer');
                            if (el) el.scrollTop = el.scrollHeight;
                        });
                    });
                    if (localStorage.getItem('puruai_started') === 'true') {
                        try {
                            const res  = await fetch('/api/check_session/' + this.sessionId);
                            const data = await res.json();
                            if (!data.valid) {
                                alert('Sesi lama Anda telah kadaluarsa (3 hari) dan dihapus otomatis oleh Server. Silakan mulai project baru.');
                                this.screen = 'setup';
                                localStorage.removeItem('puruai_started');
                                return;
                            }
                        } catch(e) { console.error('Gagal cek session', e); }
                        this.screen = 'workspace';
                        this.connectWS();
                    }
                },

                connectWS() {
                    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                    this.ws = new WebSocket(`${protocol}//${window.location.host}/ws/${this.sessionId}`);
                    this.ws.onopen = () => { this.statusText = 'Connected Server'; this.statusType = 'idle'; };
                    this.ws.onmessage = (event) => {
                        const msg = JSON.parse(event.data);
                        if (msg.type === 'chat_update')  { this.chatHistory = msg.data; }
                        else if (msg.type === 'vfs')     { this.filesList = msg.data; }
                        else if (msg.type === 'status')  {
                            this.statusText = msg.text;
                            this.statusType = msg.statusType;
                            if (msg.isLooping !== undefined) this.isLooping = msg.isLooping;
                        } else if (msg.type === 'loop_state') { this.isLooping = msg.isLooping; }
                    };
                    this.ws.onclose = () => {
                        this.statusText = 'Disconnected. Reconnecting...';
                        this.statusType = 'error';
                        setTimeout(() => this.connectWS(), 3000);
                    };
                },

                resizeTextarea(el) {
                    el.style.height = 'auto';
                    let h = el.scrollHeight;
                    if (h > 128) h = 128;
                    el.style.height = h + 'px';
                },

                startFreshProject() {
                    this.screen = 'workspace';
                    localStorage.setItem('puruai_started', 'true');
                    this.clearSession();
                    if (!this.ws || this.ws.readyState !== 1) this.connectWS();
                },

                async clearSession() {
                    const f = new FormData();
                    f.append('session_id', this.sessionId);
                    await fetch('/api/clear_session', { method: 'POST', body: f });
                    this.chatHistory = []; this.isLooping = false;
                    this.statusType = 'idle'; this.statusText = 'Idle'; this.activeTab = 'chat';
                },

                async resetAll() {
                    const f = new FormData();
                    f.append('session_id', this.sessionId);
                    await fetch('/api/delete_session', { method: 'POST', body: f });
                    localStorage.removeItem('puruai_started');
                    localStorage.removeItem('puruai_session');
                    if (this.ws) this.ws.close();
                    this.sessionId = getSessionId();
                    this.chatHistory = []; this.filesList = []; this.screen = 'setup';
                },

                async handleZipUpload(event) {
                    const file = event.target.files[0];
                    if (!file) return;
                    this.statusText = 'Uploading & Extracting...'; this.statusType = 'active';
                    const f = new FormData();
                    f.append('session_id', this.sessionId); f.append('file', file);
                    try {
                        const res = await fetch('/api/upload_zip', { method: 'POST', body: f });
                        if (res.ok) {
                            this.screen = 'workspace';
                            localStorage.setItem('puruai_started', 'true');
                            this.statusText = 'Idle'; this.statusType = 'idle';
                            if (!this.ws || this.ws.readyState !== 1) this.connectWS();
                        } else { alert('Gagal mengupload ZIP.'); }
                    } catch (err) { alert('Error: ' + err.message); }
                    event.target.value = '';
                },

                async handleContextUpload(event) {
                    const file = event.target.files[0];
                    if (!file || this.isLooping) return;
                    const f = new FormData();
                    f.append('session_id', this.sessionId); f.append('file', file);
                    try {
                        this.statusText = 'Uploading Konteks...'; this.statusType = 'active';
                        const res = await fetch('/api/upload_context', { method: 'POST', body: f });
                        if (!res.ok) alert('Gagal mengupload file konteks.');
                        this.statusText = 'Idle'; this.statusType = 'idle';
                    } catch (err) { alert('Error: ' + err.message); }
                    event.target.value = '';
                },

                sendPrompt() {
                    const val = this.userInput.trim();
                    if (!val || this.isLooping) return;
                    this.isLooping = true;
                    this.userInput = '';
                    this.$refs.chatInput.style.height = 'auto';
                    if (this.statusType === 'done') { this.statusType = 'idle'; this.statusText = 'Berpikir...'; }
                    this.ws.send(JSON.stringify({ action: 'prompt', text: val }));
                }
            }));
        });
    </script>
</body>
</html>
"""
