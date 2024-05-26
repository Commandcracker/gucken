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

-- Check if booth op and ed times are given
local has_op = options.op_start and options.op_end
local has_ed = options.ed_start and options.ed_end

while true do
	local time = get_time()

	if time then
		if has_op and not skipped_op and time >= options.op_start and time < options.op_end then
			skipped_op = set_time(options.op_end)
		end

		if has_ed and not skipped_ed and time >= options.ed_start and time < options.ed_end then
			skipped_ed = set_time(options.ed_end)
		end
	end

	vlc.misc.mwait(vlc.misc.mdate() + 2500) -- Don't waste processor time
end
