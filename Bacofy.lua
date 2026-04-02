-- ==========================================
-- PROGRAM: BACOFY ULTIMATE (V4.0 - High Performance)
-- AUTHOR:  Julian & Gemini
-- ==========================================

local speaker = peripheral.find("speaker")
local indexURL = "https://raw.githubusercontent.com/poehljulian18012000-cyber/Music/main/index.txt"

local masterPlaylists, currentSongs = {}, {}
local view, vol, currentIdx, isPlaying = "MASTER", 0.5, 1, false
local selectedPlaylistName = ""
local progress = 0
local w, h = term.getSize()

-- UI HELPER
local function drawBox(x, y, width, height, color)
    term.setBackgroundColor(color)
    for i = 0, height - 1 do
        term.setCursorPos(x, y + i)
        term.write(string.rep(" ", width))
    end
end

-- DECODER V4.0 (Anti-Noise Filter)
local function createDecoder()
    local charge, prec = 0, 0
    return function(byte)
        local out = {}
        for i = 0, 7 do
            local bit = bit32.extract(byte, i, 1) == 1
            local target = bit and 127 or -128
            local diff = target - charge
            charge = charge + bit32.arshift(diff * 48, 8) 
            if bit == (prec > 0) or (bit and prec == 0) then 
                prec = math.min(prec + 1, 12)
            else 
                prec = math.max(prec - 2, -12) 
            end
            out[i + 1] = charge
        end
        return out
    end
end

-- DATEN LADEN
local function getList(url)
    local cacheFreeUrl = url .. "?t=" .. os.epoch("utc")
    local res = http.get(cacheFreeUrl)
    if not res then return nil end
    local list = {}
    for line in res.readAll():gmatch("[^\r\n]+") do
        local l, n = line:match("^(.*),(.*)$")
        if l then table.insert(list, {url=l:gsub("%s+",""), name=n:match("^%s*(.-)%s*$")}) end
    end
    res.close()
    return list
end

-- UI ZEICHNEN
local function drawUI()
    term.setBackgroundColor(colors.black)
    term.clear()

    -- Header
    drawBox(1, 1, w, 1, colors.blue)
    term.setTextColor(colors.white)
    term.setCursorPos(2, 1)
    term.write("BACOFY PRO V4")

    -- Genre Info
    term.setBackgroundColor(colors.gray)
    term.setCursorPos(1, 2)
    term.write(string.rep(" ", w))
    term.setCursorPos(2, 2)
    term.write(view == "MASTER" and "Waehle Genre:" or "Genre: " .. selectedPlaylistName)

    -- Liste
    local displayList = (view == "MASTER") and masterPlaylists or currentSongs
    if displayList then
        for i, item in ipairs(displayList) do
            if i > h - 7 then break end
            term.setCursorPos(2, 3 + i)
            if view == "SONGS" and i == currentIdx and isPlaying then
                term.setTextColor(colors.lime)
                term.write("> " .. string.sub(item.name, 1, w-4))
            else
                term.setTextColor(colors.white)
                term.write("  " .. string.sub(item.name, 1, w-4))
            end
        end
    end

    -- Progress Bar
    if isPlaying then
        local barW = w - 4
        local fill = math.floor((progress / 100) * barW)
        term.setCursorPos(2, h-3)
        term.setBackgroundColor(colors.lightGray)
        term.write(string.rep(" ", barW))
        term.setCursorPos(2, h-3)
        term.setBackgroundColor(colors.blue)
        term.write(string.rep(" ", fill))
    end

    -- Controls Footer
    drawBox(1, h-1, w, 1, colors.gray)
    term.setTextColor(colors.white)
    term.setCursorPos(2, h-1)
    term.write("VOL:" .. math.floor(vol*100) .. "%")
    term.setCursorPos(math.floor(w/2)-2, h-1)
    term.setBackgroundColor(isPlaying and colors.red or colors.green)
    term.write(isPlaying and " STOP " or " PLAY ")
    term.setCursorPos(w-8, h-1)
    term.setBackgroundColor(colors.blue)
    term.write(view == "SONGS" and " BACK " or " REFR ")
end

-- STREAMING
local function playSong(url)
    if not speaker then return end
    local res = http.get({ url = url, binary = true })
    if not res then return end
    
    local decode = createDecoder()
    isPlaying = true
    progress = 0
    local bytesTotal = 1500000 -- Schätzwert für Progress
    local bytesRead = 0
    
    while isPlaying do
        local chunk = res.read(8192)
        if not chunk then break end
        bytesRead = bytesRead + #chunk
        progress = math.min(99, (bytesRead / bytesTotal) * 100)
        
        local buffer = {}
        for i = 1, #chunk do
            local samples = decode(chunk:byte(i))
            for j = 1, 8 do table.insert(buffer, samples[j]) end
        end
        
        while isPlaying and not speaker.playAudio(buffer, vol) do
            os.pullEvent("speaker_audio_empty")
        end
        drawUI()
        os.sleep(0)
    end
    res.close()
    if isPlaying then 
        currentIdx = (currentIdx % #currentSongs) + 1
        os.queueEvent("start_music")
    end
end

-- MAIN LOOP
masterPlaylists = getList(indexURL)
drawUI()

parallel.waitForAny(
    function() -- Input Task
        while true do
            local _, _, x, y = os.pullEvent("mouse_click")
            if y >= 4 and y <= h-4 then
                local idx = y - 3
                if view == "MASTER" and masterPlaylists[idx] then
                    selectedPlaylistName = masterPlaylists[idx].name
                    currentSongs = getList(masterPlaylists[idx].url)
                    if currentSongs then view = "SONGS" end
                elseif view == "SONGS" and currentSongs[idx] then
                    currentIdx, isPlaying = idx, false
                    os.queueEvent("start_music")
                end
            elseif y == h-1 then
                if x < 10 then vol = (vol >= 1) and 0.1 or vol + 0.1
                elseif x > w-10 then view = "MASTER"; masterPlaylists = getList(indexURL)
                else isPlaying = not isPlaying; if isPlaying then os.queueEvent("start_music") end end
            end
            drawUI()
        end
    end,
    function() -- Music Task
        while true do
            os.pullEvent("start_music")
            if currentSongs[currentIdx] then playSong(currentSongs[currentIdx].url) end
        end
    end
)