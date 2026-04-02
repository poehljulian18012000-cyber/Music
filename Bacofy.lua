-- ==========================================
-- BACOFY RAW ULTIMATE - From Scratch
-- ==========================================

-- 1. INITIALISIERUNG
local speaker = peripheral.find("speaker")
local indexURL = "https://raw.githubusercontent.com/poehljulian18012000-cyber/Music/main/index.txt"

local state = {
    view = "MASTER", -- MASTER oder SONGS
    playlists = {},
    songs = {},
    currentIdx = 1,
    volume = 0.5,
    isPlaying = false,
    status = "Bereit",
    selectedPlaylist = ""
}

local w, h = term.getSize()

-- 2. HILFSFUNKTIONEN (LOGIK)
local function fetchData(url)
    local res = http.get(url .. "?t=" .. os.epoch("utc"))
    if not res then return nil end
    local data = {}
    for line in res.readAll():gmatch("[^\r\n]+") do
        local link, name = line:match("^(.*),(.*)$")
        if link then 
            table.insert(data, {url = link:gsub("%s+", ""), name = name:match("^%s*(.-)%s*$")})
        end
    end
    res.close()
    return data
end

-- 3. DER RAW-PLAYER (DAS HERZSTÜCK)
local function playSong(url)
    if not speaker then state.status = "Kein Speaker!"; return end
    
    local res = http.get({ url = url, binary = true })
    if not res then state.status = "Download-Fehler"; return end
    
    state.isPlaying = true
    state.status = "Spiele..."
    
    while state.isPlaying do
        local chunk = res.read(8192) -- Optimaler Puffer für RAW
        if not chunk then break end
        
        local buffer = {}
        for i = 1, #chunk do
            local val = string.byte(chunk, i)
            -- RAW 8-Bit Signed Konvertierung
            if val > 127 then val = val - 256 end
            table.insert(buffer, val)
        end
        
        -- Warten, wenn Speaker-Buffer voll ist
        while state.isPlaying and not speaker.playAudio(buffer, state.volume) do
            os.pullEvent("speaker_audio_empty")
        end
        os.sleep(0)
    end
    
    res.close()
    if state.isPlaying then 
        state.currentIdx = (state.currentIdx % #state.songs) + 1
        os.queueEvent("auto_next")
    end
end

-- 4. UI-ENGINE (DESIGN)
local function draw()
    term.setBackgroundColor(colors.black)
    term.clear()
    
    -- TOP BAR
    term.setCursorPos(1, 1)
    term.setBackgroundColor(colors.gray)
    term.clearLine()
    term.setTextColor(colors.cyan)
    term.write(" BACOFY RAW ")
    term.setTextColor(colors.white)
    term.write(state.view == "MASTER" and " > Playlists" or " > " .. state.selectedPlaylist)

    -- LISTE
    local list = (state.view == "MASTER") and state.playlists or state.songs
    for i, item in ipairs(list) do
        if i > h - 4 then break end
        
        local isSelected = (state.view == "SONGS" and i == state.currentIdx and state.isPlaying)
        term.setCursorPos(2, i + 2)
        
        if isSelected then
            term.setTextColor(colors.lime)
            term.write(">> " .. item.name)
        else
            term.setTextColor(colors.white)
            term.write(i .. ". " .. item.name)
        end
    end

    -- BOTTOM BAR (CONTROLS)
    term.setCursorPos(1, h - 1)
    term.setBackgroundColor(colors.blue)
    term.clearLine()
    term.setTextColor(colors.white)
    local playLabel = state.isPlaying and " [STOP] " or " [PLAY] "
    term.write(playLabel .. " VOL: " .. math.floor(state.volume * 100) .. "% | [B] Zurück")

    -- STATUS ZEILE
    term.setCursorPos(1, h)
    term.setBackgroundColor(colors.black)
    term.setTextColor(colors.lightGray)
    term.clearLine()
    term.write(" Status: " .. state.status)
end

-- 5. EVENT-LOOP (BEDIENUNG)
local function main()
    state.playlists = fetchData(indexURL) or {}
    draw()
    
    while true do
        local event, p1, p2, p3 = os.pullEvent()
        
        if event == "mouse_click" then
            local y = p3
            if y >= 3 and y < h - 1 then
                local idx = y - 2
                if state.view == "MASTER" and state.playlists[idx] then
                    state.selectedPlaylist = state.playlists[idx].name
                    state.songs = fetchData(state.playlists[idx].url)
                    state.view = "SONGS"
                elseif state.view == "SONGS" and state.songs[idx] then
                    state.currentIdx = idx
                    state.isPlaying = false
                    os.queueEvent("start_music")
                end
            elseif y == h - 1 then -- Control Bar Click
                if p2 <= 8 then -- Play/Stop Bereich
                    if state.isPlaying then state.isPlaying = false else os.queueEvent("start_music") end
                else -- Volume Bereich
                    state.volume = (state.volume >= 1) and 0.1 or state.volume + 0.1
                end
            end
        
        elseif event == "key" then
            if p1 == keys.b then state.view = "MASTER"
            elseif p1 == keys.r then state.playlists = fetchData(indexURL) end
            
        elseif event == "start_music" or event == "auto_next" then
            parallel.waitForAny(
                function() while true do os.pullEvent(); draw() end end, -- UI Update während Play
                function() playSong(state.songs[state.currentIdx].url) end
            )
        end
        
        draw()
    end
end

-- START
main()