-- ==========================================
-- PROGRAM: BACOFY CLASSIC (V2.5 - HQ Audio)
-- AUTHOR:  Julian & Gemini
-- ==========================================

local speaker = peripheral.find("speaker")
local indexURL = "https://raw.githubusercontent.com/poehljulian18012000-cyber/Music/main/index.txt"

local masterPlaylists, currentSongs = {}, {}
local view, vol, currentIdx, isPlaying = "MASTER", 0.5, 1, false
local selectedPlaylistName = ""
local w, h = term.getSize()

-- HQ DECODER
local function createDecoder()
    local charge, prec = 0, 0
    return function(byte)
        local out = {}
        for i = 0, 7 do
            local bit = bit32.extract(byte, i, 1) == 1
            local target = bit and 127 or -128
            charge = charge + bit32.arshift((target - charge) * 48, 8) 
            if bit == (prec > 0) or (bit and prec == 0) then prec = math.min(prec + 1, 12)
            else prec = math.max(prec - 2, -12) end
            out[i + 1] = charge
        end
        return out
    end
end

-- DATEN VOM SERVER LADEN
local function getList(url)
    local res = http.get(url .. "?t=" .. os.epoch("utc"))
    if not res then return nil end
    local list = {}
    for line in res.readAll():gmatch("[^\r\n]+") do
        local l, n = line:match("^(.*),(.*)$")
        if l then table.insert(list, {url=l:gsub("%s+",""), name=n:match("^%s*(.-)%s*$")}) end
    end
    res.close()
    return list
end

-- KLASSISCHES UI DESIGN (Listen-Look)
local function drawUI()
    term.setBackgroundColor(colors.black)
    term.clear()
    term.setCursorPos(1,1)
    term.setTextColor(colors.blue)
    
    if view == "MASTER" then
        print("--- BACOFY GENRES ---")
        term.setTextColor(colors.white)
        for i, p in ipairs(masterPlaylists) do
            print(i .. ". " .. p.name)
        end
    else
        print("--- GENRE: " .. selectedPlaylistName .. " ---")
        term.setTextColor(colors.white)
        for i, s in ipairs(currentSongs) do
            if i == currentIdx and isPlaying then
                term.setTextColor(colors.lime)
                print("> " .. s.name)
                term.setTextColor(colors.white)
            else
                print(i .. ". " .. s.name)
            end
        end
    end
    
    -- Status-Leiste unten
    term.setCursorPos(1, h)
    term.setBackgroundColor(colors.gray)
    term.setTextColor(colors.white)
    term.clearLine()
    local status = isPlaying and "Spielt..." or "Gestoppt"
    term.write(status .. " | VOL: " .. math.floor(vol*100) .. "% | [B] ZURUECK")
    term.setBackgroundColor(colors.black)
end

-- AUDIO STREAMING
local function playSong(url)
    if not speaker then return end
    local res = http.get({ url = url, binary = true })
    if not res then return end
    
    local decode = createDecoder()
    isPlaying = true
    
    while isPlaying do
        local chunk = res.read(4096)
        if not chunk then break end
        
        local buffer = {}
        for i = 1, #chunk do
            local samples = decode(chunk:byte(i))
            for j = 1, 8 do table.insert(buffer, samples[j]) end
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

-- INITIALISIERUNG
masterPlaylists = getList(indexURL)
drawUI()

-- MULTI-TASKING
parallel.waitForAny(
    function() -- Tastatur Steuerung
        while true do
            local event, key = os.pullEvent("key")
            if key == keys.b then
                view = "MASTER"
            elseif key == keys.r then
                masterPlaylists = getList(indexURL)
            elseif key >= keys.one and key <= keys.nine then
                local num = key - 1
                if view == "MASTER" and masterPlaylists[num] then
                    selectedPlaylistName = masterPlaylists[num].name
                    currentSongs = getList(masterPlaylists[num].url)
                    if currentSongs then view = "SONGS" end
                elseif view == "SONGS" and currentSongs[num] then
                    currentIdx = num
                    isPlaying = false -- Reset aktuellen Song
                    os.queueEvent("start_music")
                end
            elseif key == keys.space then
                isPlaying = not isPlaying
                if isPlaying then os.queueEvent("start_music") end
            end
            drawUI()
        end
    end,
    function() -- Musik Steuerung
        while true do
            os.pullEvent("start_music")
            if currentSongs[currentIdx] then
                playSong(currentSongs[currentIdx].url)
            end
        end
    end
)