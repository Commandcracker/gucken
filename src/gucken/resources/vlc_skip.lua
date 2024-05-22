-- Returns time in microseconds or nil if not found
local function get_time()
	local input = vlc.object.input()
	if input then
		return vlc.var.get(input, "time")
	end
end

-- Returns true if successful and false if not
local function set_time(microseconds)
	local input = vlc.object.input()
	if input then
		vlc.var.set(input, "time", microseconds)
		return true
	end
	return false
end

-- Get timings form options and converts them to microseconds
local function get_time_option(key)
	time = tonumber(config[key])
	if time then
		return time * 1000000
	end
end

-- Get timings from options
local options = {
	op_start = get_time_option("op_start"),
	op_end = get_time_option("op_end"),
	ed_start = get_time_option("ed_start"),
	ed_end = get_time_option("ed_end"),
}

-- Vals to only skip once
local skipped_op = false
local skipped_ed = false

-- Check if booth op times are given
local has_op = false
if options.op_start and options.op_end then
	has_op = true
else
	-- No op = already skipped
	skipped_op = true
end
-- Check if booth ed times are given
local has_ed = false
if options.ed_start and options.ed_end then
	has_ed = true
else
	-- No ed = already skipped
	skipped_ed = true
end

-- Exit if no timings are specified
if not has_op and not has_ed then
	return
end

while true do
	local time = get_time()

	if time then
		-- This is captured by gucken
		--print("TIME:", time)

		if not skipped_op and time >= options.op_start and time < options.op_end then
			skipped_op = set_time(options.op_end)
		end

		if not skipped_ed and time >= options.ed_start and time < options.ed_end then
			skipped_ed = set_time(options.ed_end)
		end
	end

	-- Exit when all skips are finished
	if skipped_op == true and skipped_ed == true then
		return
	end

	vlc.misc.mwait(vlc.misc.mdate() + 2500) -- Don't waste processor time
end

--[[ load form one script
-- TODO: only load syncplay when it should load

-- Add intf path to package.path, so require can find syncplay
local file_path = debug.getinfo(1, "S").source:sub(2)
local separator = '/'
if string.find(file_path, '\\') then separator = '\\' end

local parts = {}
for part in string.gmatch(file_path, "[^" .. separator .. "]+") do
	table.insert(parts, part)
end
table.remove(parts, #parts)
local intf_path = table.concat(parts, separator)

package.path = intf_path..separator.."?.lua;"..package.path

-- Add coroutine.yield() to custom mwait
original_mwait = vlc.misc.mwait

function custom_mwait(microseconds)
	coroutine.yield()
    -- booth syncplay and skip wait 2500 microseconds,
    -- so we just halt that on booth of them and then they still wait the sme time
	original_mwait(microseconds-1250)
end

-- Inject the custom mwait function
_G = setmetatable({}, {
    __index = function(self, key)
        if key == "vlc" then
            return setmetatable({}, {
                __index = function(self, key)
                    if key == "misc" then
                        return setmetatable({}, {
                            __index = function(self, key)
                                if key == "mwait" then return custom_mwait end
                                return self[key]
                            end,
                        })
                    end
                    return self[key]
                end,
            })
        end
        return self[key]
    end,
})

-- TODO: get and inject syncplay config
local function syncplay() require("syncplay") end

local skip_coroutine = coroutine.create(main)
local syncplay_coroutine = coroutine.create(syncplay)

while coroutine.status(skip_coroutine) ~= "dead" or coroutine.status(syncplay_coroutine) ~= "dead" do
    if coroutine.status(skip_coroutine) ~= "dead" then
        coroutine.resume(skip_coroutine)
    end
    if coroutine.status(syncplay_coroutine) ~= "dead" then
        coroutine.resume(syncplay_coroutine)
    end
end

-- TODO: fix vlc sometimes not quitting
]]
