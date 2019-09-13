// 水準器

var Level = function() {
  this.visible = true;
  this.acc = null;
  this.canvas = document.querySelector("#levelCanvas");
  this.ctx = this.canvas.getContext("2d");
  this.canvas.width = 320;
  this.canvas.height = 400;
  window.addEventListener("devicemotion", this.motion.bind(this), true);
};

// 加速度の取得
Level.prototype.motion = function(event) {
  // return function(event){
  var acc = event.accelerationIncludingGravity;
  this.acc = {};
  this.acc.gx = acc.x;
  this.acc.gy = acc.y;
  this.acc.gz = acc.z;
  var userAgent = window.navigator.userAgent;
  if (
    userAgent.indexOf("iPhone") > 0 ||
    userAgent.indexOf("iPad") > 0 ||
    userAgent.indexOf("iPod") > 0
  ) {
    this.acc.gx *= -1;
    this.acc.gy *= -1;
    this.acc.gz *= -1;
  }
  // };
};

// 水平器カーソルを描画
Level.prototype.draw = function() {
  if (this.visible == false) return;

  this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

  this.ctx.shadowColor = "#000";
  this.ctx.shadowBlur = 0;
  this.ctx.font = "12px 'Arial',sans-serif";

  // 水平器の中心
  var x = 0,
    y = 0;
  this.ctx.strokeStyle = "#000";
  this.ctx.fillStyle = "#0f0";
  // 加速度センサーの判定別処理
  if ("ondevicemotion" in window && this.acc != null) {
    var gravity = 9.8;
    x = (this.acc.gx / gravity) * (90 / 2 - 5);
    y = (this.acc.gy / gravity) * (90 / 2 - 5);
  } else {
    // 加速度センサーの取得に失敗
    this.ctx.strokeStyle = "#000";
    this.ctx.fillStyle = "#f44";
  }
  // カーソル描画
  this.ctx.lineWidth = 2;
  this.ctx.beginPath();
  this.ctx.arc(
    this.canvas.width / 2 + x,
    this.canvas.height / 2 - y,
    5,
    0,
    2 * Math.PI,
    true
  );
  this.ctx.stroke();
  this.ctx.fill();
  // 水準器のカーソル座標
  this.ctx.textAlign = "center";
  drawBorderText(this.ctx, " y:" + y.toFixed(1), this.canvas.width / 2, 150, 4);
  this.ctx.textAlign = "start";
  drawBorderText(this.ctx, "x:" + x.toFixed(1), 205, this.canvas.height / 2, 4);
};

Level.prototype.show = function() {
  var levelArea = document.querySelector("#level-bg");
  var canvasArea = document.querySelector("#levelCanvas");
  var levelButton = document.querySelector("#btn-level");
  this.visible = !this.visible;
  levelArea.style.visibility = 
  canvasArea.style.visibility = this.visible ? "visible" : "hidden";
  levelButton.innerHTML = this.visible ? "水準器あり" : "水準器なし";
};
