// 時計ライブラリ

// 時計の壁紙ファイル
var wallpaper = [
  "wallpaper/tukikage.png",
  "wallpaper/jtwp_fwvga.jpg",
  "wallpaper/air_240x400.png",
  "wallpaper/mog2_240x400.png"
];

function drawBorderText(ctx, text, x, y, lineWidth) {
  ctx.lineWidth = lineWidth;
  ctx.strokeText(text, x, y);
  ctx.fillText(text, x, y);
}

var Clock = function() {
  this.wallpapers = [];
  this.analog = true;
  this.wpIndex = -1;
  this.smoothHand = true;

  this.canvas = document.querySelector("#clockCanvas");
  this.ctx = this.canvas.getContext("2d");
  this.canvas.width = 320;
  this.canvas.height = 400;
  this.level = new Level();
};

// 壁紙のファイル設定
Clock.prototype.setWallpapers = function(files) {
  this.wallpapers = files;
};
Clock.prototype.addWallpaper = function(file) {
  this.wallpapers.push();
};

Clock.prototype.start = function() {
  this.nextWallpaper();
  requestAnimationFrame(this.update.bind(this));
};

Clock.prototype.update = function(timeStamp) {
  var timer = requestAnimationFrame(this.update.bind(this));

  this.updateHands();

  // 描画処理
  this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
  this.ctx.shadowColor = "#000";
  this.ctx.shadowBlur = 2;
  this.ctx.textAlign = "center";
  this.ctx.textBaseline = "middle";

  var fontFamily =
    "YuGothic,'Yu Gothic','ヒラギノ角ゴシック','Hiragino Sans',sans-serif";
  this.ctx.fillStyle = "#fff";
  this.ctx.strokeStyle = "#000";
  // 今日の日付
  var today = this.getToday();
  this.ctx.font = "14px " + fontFamily;
  drawBorderText(this.ctx, today.year, 40, 20, 5);
  this.ctx.font = "24px " + fontFamily;
  drawBorderText(this.ctx, today.day, this.canvas.width / 2, 20, 5);
  this.ctx.font = "20px " + fontFamily;
  drawBorderText(this.ctx, today.week, 280, 20, 5);
  // 現在時刻
  var time = this.getTime();
  this.ctx.shadowBlur = 3;
  this.ctx.font = "bold 30px " + fontFamily;
  drawBorderText(this.ctx, time, this.canvas.width / 2, 272, 5);
  // 水準器の描画
  this.level.draw();
};

// 今日の日付をテキストで取得
Clock.prototype.getToday = function() {
  // 日時の取得
  var date = new Date();
  var year = date.getFullYear();
  var mon = date.getMonth() + 1;
  var week = ["日", "月", "火", "水", "木", "金", "土"][date.getDay()];
  var day = date.getDate();
  var md = mon + "月" + day + "日";

  return {
    year: year + "年 ",
    day: mon + "月" + day + "日 ",
    week: week + "曜日"
  };
};

// 現在時刻をテキストで取得
Clock.prototype.getTime = function() {
  // 時刻の取得
  var date = new Date();
  var hh = date.getHours();
  var mm = date.getMinutes();
  if (mm < 10) {
    mm = "0" + mm;
  }
  var ss = date.getSeconds();
  if (ss < 10) {
    ss = "0" + ss;
  }
  return hh + " : " + mm;
};

// 時計の針を回転させる
Clock.prototype.updateHands = function() {
  var date = new Date();
  var h, m, s;

  if (this.smoothHand) {
    // 針の動き (無段階)
    var jst = date - date.getTimezoneOffset() * 60 * 1000;
    h = (jst / 1000 / 60 / 60) % 24;
    m = (jst / 1000 / 60) % 60;
    s = (jst / 1000) % 60;
  } else {
    // 針の動き (飛び飛び)
    h = date.getHours();
    m = date.getMinutes();
    s = date.getSeconds();
  }

  // 時針 θ=π(t/6-0.5)
  var hAngle = Math.PI * (h / 6 - 0.5);
  // 分針・秒針 θ=π(t/30-0.5)
  var mAngle = Math.PI * (m / 30 - 0.5);
  var sAngle = Math.PI * (s / 30 - 0.5);

  // css3: transform:rotate(180deg);
  var hHand = document.getElementById("h-hand");
  var mHand = document.getElementById("m-hand");
  var sHand = document.getElementById("s-hand");
  hHand.style.transform = hHand.style.webkitTransform =
    "rotate(" + hAngle + "rad)";
  mHand.style.transform = mHand.style.webkitTransform =
    "rotate(" + mAngle + "rad)";
  sHand.style.transform = sHand.style.webkitTransform =
    "rotate(" + sAngle + "rad)";
};

// アナログ・デジタルの表示切り替え
Clock.prototype.mode = function() {
  var modeButton = document.querySelector("#btn-clockMode");
  var dialArea = document.querySelector("#dial");
  var handsArea = document.querySelector("#hands");
  this.analog = !this.analog;
  if (this.analog) {
    dialArea.style.display = handsArea.style.display = "block";
  } else {
    dialArea.style.display = handsArea.style.display = "none";
  }
  modeButton.innerHTML = this.analog ? "アナログ" : "デジタル";
};

// 壁紙を切り替える
Clock.prototype.nextWallpaper = function() {
  if (!this.wallpapers) return;
  var wpArea = document.querySelector("#clock-bg");
  this.wpIndex = (this.wpIndex + 1) % this.wallpapers.length;
  wpArea.style.backgroundImage = "url('" + this.wallpapers[this.wpIndex] + "')";
};

// 時計の動きをなめらかにする
Clock.prototype.smooth = function() {
  var smoothButton = document.querySelector("#btn-smooth");
  this.smoothHand = !this.smoothHand;
  smoothButton.innerHTML = this.smoothHand ? "スムーズ" : "ラフ";
};
