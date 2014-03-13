var Log = function(level) {
    this.level = level;
    this.levels = {"debug": 30, "warn": 20, "info": 10};
    this.active_debug = this.level >= this.levels.debug ? this.logger : this.null_logger;
    this.active_warn = this.level >= this.levels.warn ? this.logger : this.null_logger;
    this.active_info = this.level >= this.levels.info ? this.logger : this.null_logger;
}
Log.prototype.logger = function(lvl,msg) {
    console.log("[" + lvl + "] " + new Date() + ": " + msg);
}
Log.prototype.html_logger = function(lvl,msg) {
    document.write("<p><i>" + lvl + ": " + msg + "</i></p>");
}
Log.prototype.null_logger = function(lvl,msg) {
    return true;
}
Log.prototype.warn = function warn(msg) {
    this.active_warn("WARN", msg);
}
Log.prototype.debug = function debug(msg) {
    this.active_debug("DEBUG", msg);
}
Log.prototype.info = function info(msg) {
    this.active_info("INFO", msg);
}
var log = new Log(0);
