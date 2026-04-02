-- ==========================================
-- BACOFY POCKET (RAW HQ Edition)
-- ==========================================
local speaker = peripheral.find("speaker")
local indexURL = "https://raw.githubusercontent.com/poehljulian18012000-cyber/Music/main/index.txt"

local masterPlaylists, currentSongs = {}, {}
local view, vol, currentIdx, isPlaying = "MASTER", 0.5, 1, false
local selectedPlaylistName = ""
local logs = {}

local w, h = term.getSize()

-- (Der alte Decoder wurde entfernt, da wir jetzt RAW 8-Bit nutzen)

local function log(msg, color)
    table.insert(logs, { text = msg, col = color or colors.yellow })
    if #logs > 4 then table.remove(logs, 1) end
end

local function drawUI()
    term.setBackgroundColor(colors.black)
    term.clear()
    
    -- Header
    term.setCursorPos(1, 1)
    term.setTextColor(colors.cyan)
    term.write(view == "MASTER" and "--- POCKET B-PRO ---" or "--- SONGS ---")
    
    -- Liste (Kompakt für Pocket)
    local displayList = (view == "MASTER") and masterPlaylists or currentSongs
    if displayList then
        for i, item in ipairs(displayList) do
            if i > h - 8 then break end
            local isCurrent = (view == "SONGS" and i == currentIdx and isPlaying)
            term.setBackgroundColor(isCurrent and colors.lime or (view == "MASTER" and colors.purple or colors.blue))
            term.setTextColor(isCurrent and colors.black or colors.white)
            term.setCursorPos(1, 1 + i)
            term.write(string.sub(i .. "." .. item.name, 1, w))
        end
    end
    
    -- Controls am unteren Rand
    term.setBackgroundColor(colors.gray)
    term.setTextColor(colors.white)
    term.setCursorPos(1, h-2)
    term.write(view == "SONGS" and " [BACK] " or " [REFRESH] ")
    term.write(" VOL: " .. math.floor(vol*100) .. "%")

    term.setCursorPos(1, h-1)
    term.setBackgroundColor(colors.red)
    term.write(" << ")
    term.setBackgroundColor(isPlaying and colors.orange or colors.green)
    term.setTextColor(colors.black)
    term.write(isPlaying and " STOP " or " PLAY ")
    term.setBackgroundColor(colors.red)
    term.setTextColor(colors.white)
    term.write(" >> ")
    
    -- Mini-Log
    if logs[#logs] then
        term.setBackgroundColor(colors.black)
        term.setTextColor(logs[#logs].col)
        term.setCursorPos(1, h)
        term.write("> " .. string.sub(logs[#logs].text, 1, w-2))
    end
end

-- NEUE RAW-PLAY LOGIK (Angepasst für Pocket)
local function playSong(url)
    if not speaker then log("No Speaker!", colors.red) return end
    
    local res = http.get({ url = url:gsub("%s+", ""), binary = true })
    if not res then log("404 Error", colors.red) return end
    
    isPlaying = true
    log("Playing RAW...", colors.lime)
    
    while isPlaying do
        -- Größerer Chunk (8192) für flüssigeres RAW-Streaming
        local chunk = res.read(8192)
        if not chunk then break end
        
        local buffer = {}
        for i = 1, #chunk do
            -- Byte lesen und für Speaker-Format (-128 bis 127) umrechnen
            local val = string.byte(chunk, i)
            if val > 127 then val = val - 256 end
            table.insert(buffer, val)
        end
        
        while isPlaying and not speaker.playAudio(buffer, vol) do
            os.pullEvent("speaker_audio_empty")
        end
        os.sleep(0)
    end
    res.close()
    if isPlaying then 
        currentIdx = (currentIdx % #currentSongs) + 1
        os.queueEvent("start_music")
    end
end

local function getList(url)
    local res = http.get(url)
    if not res then return nil end
    local list = {}
    for line in res.readAll():gmatch("[^\r\n]+") do
        local l, n = line:match("^(.*),(.*)$")
        if l then table.insert(list, {url=l:gsub("%s+",""), name=n:match("^%s*(.-)%s*$")}) end
    end
    res.close()
    return list
end

local function inputTask()
    while true do
        local _, _, x, y = os.pullEvent("mouse_click")
        
        if y >= 2 and y <= h-3 then
            local choice = y - 1
            if view == "MASTER" and masterPlaylists[choice] then
                selectedPlaylistName = masterPlaylists[choice].name
                currentSongs = getList(masterPlaylists[choice].url)
                if currentSongs then view = "SONGS" end
            elseif view == "SONGS" and currentSongs[choice] then
                currentIdx, isPlaying = choice, false
                os.queueEvent("start_music")
            end
        elseif y == h-2 then
            if x <= 8 then view = "MASTER" 
            elseif x >= 10 then vol = (vol + 0.1 > 1) and 0.1 or vol + 0.1 end
        elseif y == h-1 then
            if x <= 4 then -- Prev
                isPlaying = false
                currentIdx = currentIdx - 1
                if currentIdx < 1 then currentIdx = #currentSongs end
                os.queueEvent("start_music")
            elseif x <= 11 then -- Play/Stop
                if isPlaying then isPlaying = false else os.queueEvent("start_music") end
            elseif x <= 15 then -- Next
                isPlaying = false
                currentIdx = (currentIdx % #currentSongs) + 1
                os.queueEvent("start_music")
            end
        end
        drawUI()
    end
end

log("Pocket Boot...", colors.cyan)
masterPlaylists = getList(indexURL)
drawUI()

parallel.waitForAny(
    inputTask,
    function()
        while true do
            os.pullEvent("start_music")
            playSong(currentSongs[currentIdx].url)
        end
    end
)