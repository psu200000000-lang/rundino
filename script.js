(() => {
    const canvas = document.getElementById('gameCanvas');
    const ctx = canvas.getContext('2d');
    const scoreEl = document.getElementById('score');
    const highEl = document.getElementById('highscore');

    // High DPI scaling
    function setupCanvas() {
        const dpr = window.devicePixelRatio || 1;
        const w = canvas.width;
        const h = canvas.height;
        canvas.style.width = w + 'px';
        canvas.style.height = h + 'px';
        canvas.width = w * dpr;
        canvas.height = h * dpr;
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
        // pixelated rendering
        canvas.classList.add('pixelated');
        ctx.imageSmoothingEnabled = false;
    }
    setupCanvas();

    // Game vars
    const GROUND_Y = 160;
    const GRAVITY = 1300; // px/s^2
    const JUMP_V = -470; // px/s
    const DINO_W = 44; const DINO_H = 44;
    let obstacles = [];
    let spawnTimer = 0;
    const baseSpawn = 1.3; // base spawn seconds
    const baseSpeed = 280; // base obstacle speed px/s
    let spawnInterval = baseSpawn;
    let speed = baseSpeed;
    let score = 0;
    let highscore = parseInt(localStorage.getItem('dino-high')||'0',10) || 0;
    highEl.textContent = highscore;

    let running = true;

    // Difficulty settings
    const difficulties = {
        easy: { speedMul: 0.8, spawnMul: 1.25 },
        normal: { speedMul: 1.0, spawnMul: 1.0 },
        hard: { speedMul: 1.35, spawnMul: 0.75 }
    };
    let difficulty = 'normal';

    function applyDifficulty() {
        const d = difficulties[difficulty] || difficulties.normal;
        speed = baseSpeed * d.speedMul;
        spawnInterval = baseSpawn * d.spawnMul;
        // update active button UI
        document.querySelectorAll('.diff-btn').forEach(b => b.classList.toggle('active', b.dataset.diff === difficulty));
    }

    const player = {
        x: 48,
        y: GROUND_Y - DINO_H,
        w: DINO_W,
        h: DINO_H,
        vy: 0,
        grounded: true,
        jump() {
            if (this.grounded) {
                this.vy = JUMP_V;
                this.grounded = false;
            }
        },
        update(dt) {
            this.vy += GRAVITY * dt;
            this.y += this.vy * dt;
            if (this.y >= GROUND_Y - this.h) {
                this.y = GROUND_Y - this.h;
                this.vy = 0;
                this.grounded = true;
            }
        },
        draw(ctx) {
            // draw pixel sprite scaled to player size
            if (dinoSprite) {
                ctx.imageSmoothingEnabled = false;
                ctx.drawImage(dinoSprite, 0, 0, dinoSprite.width, dinoSprite.height, Math.round(this.x), Math.round(this.y), this.w, this.h);
            } else {
                ctx.fillStyle = '#eaeaea';
                ctx.fillRect(Math.round(this.x), Math.round(this.y), this.w, this.h);
            }
        }
    };

    class Obstacle {
        constructor(x, w, h, speed) {
            this.x = x; this.w = w; this.h = h; this.y = GROUND_Y - h; this.speed = speed;
        }
        update(dt) {this.x -= this.speed * dt}
        draw(ctx) {ctx.fillStyle = '#eaeaea'; ctx.fillRect(this.x, this.y, this.w, this.h)}
    }

    // create a small pixel-art dino sprite on an offscreen canvas
    let dinoSprite = null;
    function createDinoSprite() {
        const sw = 16, sh = 16; // sprite pixels
        const s = document.createElement('canvas');
        s.width = sw; s.height = sh;
        const sc = s.getContext('2d');
        sc.imageSmoothingEnabled = false;
        // transparent background
        sc.clearRect(0,0,sw,sh);
        // simple green dino pixels (hand-crafted)
        const G = '#93c47d';
        const O = '#38761d';
        const B = '#000000';
        // body blocks (x,y)
        const px = (x,y,color) => { sc.fillStyle = color; sc.fillRect(x,y,1,1); };
        // outline
        [[3,6],[4,5],[5,4],[6,4],[7,4],[8,5],[9,6],[10,6],[11,7],[11,8],[10,9],[9,10],[8,10],[7,10],[6,10],[5,10],[4,9],[3,8]].forEach(p=>px(p[0],p[1],O));
        // fill body
        for(let yy=6; yy<=9; yy++) for(let xx=5; xx<=9; xx++) px(xx,yy,G);
        // legs
        px(6,11,G); px(8,11,G);
        // eye
        px(9,6,B);
        dinoSprite = s;
    }
    createDinoSprite();

    function spawnObstacle() {
        const rnd = Math.random();
        let w = 20; let h = 40;
        if (rnd < 0.35) { w = 14; h = 28 }
        else if (rnd < 0.7) { w = 28; h = 40 }
        else { w = 40; h = 44 }
        const x = canvas.width / (window.devicePixelRatio || 1) + 10;
        obstacles.push(new Obstacle(x, w, h, speed));
    }

    function rectsOverlap(a, b) {
        return a.x < b.x + b.w && a.x + a.w > b.x && a.y < b.y + b.h && a.y + a.h > b.y;
    }

    function resetGame() {
        obstacles = [];
        spawnTimer = 0;
        // keep selected difficulty but reset base timing/speed
        applyDifficulty();
        score = 0;
        scoreEl.textContent = '0';
        player.y = GROUND_Y - player.h; player.vy = 0; player.grounded = true;
        running = true;
        lastTime = performance.now();
        loop(lastTime);
    }

    function endGame() {
        running = false;
        if (score > highscore) {
            highscore = Math.floor(score);
            localStorage.setItem('dino-high', highscore);
            highEl.textContent = highscore;
        }
        // draw game over text
        ctx.fillStyle = '#ff7b7b';
        ctx.font = '20px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText('게임 오버 - Enter 키로 재시작', canvas.width/ (window.devicePixelRatio||1) /2, 90);
    }

    // Input
    window.addEventListener('keydown', (e) => {
        if (e.code === 'Space' || e.code === 'ArrowUp') { e.preventDefault(); player.jump(); }
        if (!running && e.code === 'Enter') { resetGame(); }
    });
    canvas.addEventListener('mousedown', () => { if (running) player.jump(); else resetGame(); });
    canvas.addEventListener('touchstart', (e) => { e.preventDefault(); if (running) player.jump(); else resetGame(); }, {passive:false});

    // Difficulty button handlers
    document.querySelectorAll('.diff-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            difficulty = btn.dataset.diff || 'normal';
            applyDifficulty();
        });
    });
    // apply default at start
    applyDifficulty();

    // Loop
    let lastTime = performance.now();
    function loop(t) {
        const dt = Math.min(1/30, (t - lastTime) / 1000);
        lastTime = t;
        update(dt);
        render();
        if (running) requestAnimationFrame(loop);
    }

    function update(dt) {
        // difficulty scaling
        score += dt * 10;
        scoreEl.textContent = Math.floor(score);
        if (score > 0 && score % 100 === 0) {
            // increase speed slowly
            speed = 280 + Math.floor(score/100) * 18;
        }

        player.update(dt);
        // spawn
        spawnTimer += dt;
        if (spawnTimer > spawnInterval) {
            spawnTimer = 0;
            spawnInterval = 0.9 + Math.random() * 1.2;
            spawnObstacle();
        }

        // update obstacles
        for (let i = obstacles.length -1; i >=0; i--) {
            const ob = obstacles[i];
            ob.update(dt);
            if (ob.x + ob.w < -50) obstacles.splice(i,1);
            // collision
            if (rectsOverlap(player, ob)) {
                endGame();
            }
        }
    }

    function render() {
        const w = canvas.width / (window.devicePixelRatio || 1);
        const h = canvas.height / (window.devicePixelRatio || 1);
        ctx.clearRect(0,0,w,h);
        // ground
        ctx.fillStyle = '#222';
        ctx.fillRect(0, GROUND_Y + 6, w, 4);

        // draw player
        player.draw(ctx);

        // draw obstacles
        obstacles.forEach(ob => {
            ctx.fillStyle = '#eaeaea';
            ctx.fillRect(Math.round(ob.x), Math.round(ob.y), ob.w, ob.h);
        });

        // score (small)
        ctx.fillStyle = '#9aa0a6';
        ctx.font = '12px sans-serif';
        ctx.textAlign = 'right';
        ctx.fillText('점수: ' + Math.floor(score), w - 8, 16);
        if (!running) {
            ctx.fillStyle = '#ff7b7b';
            ctx.font = '18px sans-serif';
            ctx.textAlign = 'center';
            ctx.fillText('게임 오버 - Enter: 재시작', w/2, h/2 - 10);
        }
    }

    // start
    loop(lastTime);

})();
