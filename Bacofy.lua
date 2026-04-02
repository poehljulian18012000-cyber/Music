-- ==========================================
-- PROGRAM: BACOFY (HQ AUDIO + ORIGINAL DESIGN)
-- ==========================================

local speaker = peripheral.find("speaker")
local indexURL = "https://raw.githubusercontent.com/poehljulian18012000-cyber/Music/main/index.txt"

local masterPlaylists, currentSongs = {}, {}
local view, vol, currentIdx, isPlaying = "MASTER", 0.5, 1, false
local selectedPlaylistName = ""
local w, h = term.getSize()

-- HQ DECODER (SMOOTH TRANSITION)
local function createDecoder()
    local charge, prec = 0, 0
    return function(byte)
        local out = {}
        for i = 0, 7 do
            local bit = bit32.extract(byte, i, 1) == 1
            local target = bit and 127 or -128
            -- Smoothing Filter
            charge = charge + bit32.arshift((target - charge) * 48, 8) 
            if bit == (prec > 0) or (bit and prec == 0) then prec = math.min(prec + 1, 12)
            else prec = math.max(prec - 2, -12) end
            out[i + 1] = charge
        end
        return out
    end
end

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

local function drawUI()
    term.setBackgroundColor(colors.black)
    term.clear()
    
    -- Header
    term.setCursorPos(1, 1)
    term.setBackgroundColor(colors.blue)
    term.clearLine()
    local header = "BACOFY MUSIC"
    term.setCursorPos(math.floor((w - #header) / 2) + 1, 1)
    term.write(header)

    -- Liste
    term.setBackgroundColor(colors.black)
    local displayList = (view == "MASTER") and masterPlaylists or currentSongs
    if displayList then
        for i, item in ipairs(displayList) do
            if i > h - 3 then break end
            term.setCursorPos(2, 2 + i)
            if view == "SONGS" and i == currentIdx and isPlaying then
                term.setTextColor(colors.lime)
                term.write("> " .. item.name)
            else
                term.setTextColor(colors.white)
                term.write(i .. ". " .. item.name)
            end
        end
    end

    -- Footer
    term.setCursorPos(1, h)
    term.setBackgroundColor(colors.gray)
    term.clearLine()
    term.setTextColor(colors.white)
    term.write(" VOL: " .. math.floor(vol*100) .. "% | [B] BACK | [R] REFRESH")
end

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

masterPlaylists = getList(indexURL)
drawUI()

parallel.waitForAny(
    function() -- Klick-Logik
        while true do
            local _, _, x, y = os.pullEvent("mouse_click")
            if y >= 3 and y < h then
                local idx = y - 2
                if view == "MASTER" and masterPlaylists[idx] then
                    selectedPlaylistName = masterPlaylists[idx].name
                    currentSongs = getList(masterPlaylists[idx].url)
                    view = "SONGS"
                elseif view == "SONGS" and currentSongs[idx] then
                    currentIdx = idx
                    isPlaying = false
                    os.queueEvent("start_music")
                end
            end
            drawUI()
        end
    end,
    function() -- Tasten-Logik
        while true do
            local _, key = os.pullEvent("key")
            if key == keys.b then view = "MASTER"
            elseif key == keys.r then masterPlaylists = getList(indexURL) end
            drawUI()
        end
    end,
    function() -- Musik Task
        while true do
            os.pullEvent("start_music")
            if currentSongs[currentIdx] then playSong(currentSongs[currentIdx].url) end
        end
    end
)