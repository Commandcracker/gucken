local mpv_utils = require("mp.utils")

-- Stop script if skip.lua is inside scripts folder
local scripts_dir = mp.find_config_file("scripts")
if scripts_dir ~= nil and mpv_utils.file_info(mpv_utils.join_path(scripts_dir, "skip.lua")) ~= nil then
	mp.msg.info("Disabling, another skip.lua is already present in scripts dir")
	return
end

local mpv_options = require("mp.options")

local options = {
	op_start = 0,
	op_end = 0,
	ed_start = 0,
	ed_end = 0,
}
mpv_options.read_options(options, "skip")

local skipped_op = false
local skipped_ed = false

local function check_skip()
	local current_time = mp.get_property_number("time-pos")
	if not current_time then
		return
	end

	-- Opening
	if not skipped_op and current_time >= options.op_start and current_time < options.op_end then
		mp.set_property_number("time-pos", options.op_end)
		skipped_op = true
	end

	-- Ending
	if not skipped_ed and current_time >= options.ed_start and current_time < options.ed_end then
		mp.set_property_number("time-pos", options.ed_end)
		skipped_ed = true
	end
end

mp.observe_property("time-pos", "number", check_skip)
