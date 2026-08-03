/* ==========================================================
   HNNYMOTION OFFICIAL
   LANDING PAGE
   PART 1
========================================================== */

const canvas = document.getElementById("stars");
const ctx = canvas.getContext("2d");

let width;
let height;

function resizeCanvas(){

    width = canvas.width = window.innerWidth;

    height = canvas.height = window.innerHeight;

}

resizeCanvas();

window.addEventListener("resize",resizeCanvas);


/* ==========================================
        STARS
========================================== */

const STAR_COUNT = window.innerWidth < 768 ? 120 : 220;

const stars = [];

class Star{

    constructor(){

        this.reset();

    }

    reset(){

        this.x=Math.random()*width;

        this.y=Math.random()*height;

        this.radius=Math.random()*2.5;

        this.alpha=Math.random();

        this.speed=Math.random()*0.5+0.15;

    }

    update(){

        this.alpha += this.speed*0.02;

        if(this.alpha>=1){

            this.speed*=-1;

        }

        if(this.alpha<=0){

            this.speed*=-1;

        }

    }

    draw(){

        ctx.beginPath();

        ctx.arc(

            this.x,

            this.y,

            this.radius,

            0,

            Math.PI*2

        );

        ctx.fillStyle=

        `rgba(255,255,255,${this.alpha})`;

        ctx.fill();

    }

}

for(let i=0;i<STAR_COUNT;i++){

    stars.push(new Star());

}


/* ==========================================
            SHOOTING STAR
========================================== */

const shootingStars=[];

class ShootingStar{

    constructor(){

        this.reset();

    }

    reset(){

        this.x=Math.random()*width;

        this.y=Math.random()*200;

        this.length=Math.random()*120+100;

        this.speed=Math.random()*8+8;

        this.opacity=1;

    }

    update(){

        this.x+=this.speed;

        this.y+=this.speed*.4;

        this.opacity-=0.008;

        if(this.opacity<=0){

            this.reset();

        }

    }

    draw(){

        ctx.beginPath();

        ctx.moveTo(

            this.x,

            this.y

        );

        ctx.lineTo(

            this.x-this.length,

            this.y-this.length*.4

        );

        ctx.strokeStyle=

        `rgba(255,255,255,${this.opacity})`;

        ctx.lineWidth=2;

        ctx.stroke();

    }

}

setInterval(()=>{

    if(shootingStars.length<3){

        shootingStars.push(

            new ShootingStar()

        );

    }

},5000);


/* ==========================================
          PARTICLES
========================================== */

const particles=[];

class Particle{

    constructor(){

        this.x=Math.random()*width;

        this.y=Math.random()*height;

        this.size=Math.random()*3;

        this.speedX=Math.random()-.5;

        this.speedY=Math.random()-.5;

    }

    update(){

        this.x+=this.speedX;

        this.y+=this.speedY;

        if(this.x<0) this.x=width;

        if(this.x>width) this.x=0;

        if(this.y<0) this.y=height;

        if(this.y>height) this.y=0;

    }

    draw(){

        ctx.beginPath();

        ctx.arc(

            this.x,

            this.y,

            this.size,

            0,

            Math.PI*2

        );

        ctx.fillStyle="rgba(0,212,255,.15)";

        ctx.fill();

    }

}

for(let i=0;i<80;i++){

    particles.push(

        new Particle()

    );

}
/* ==========================================
        ANIMATION LOOP
========================================== */

function animate(){

    ctx.clearRect(0,0,width,height);

    stars.forEach(star=>{

        star.update();

        star.draw();

    });

    particles.forEach(p=>{

        p.update();

        p.draw();

    });

    shootingStars.forEach((s,index)=>{

        s.update();

        s.draw();

        if(s.opacity<=0){

            shootingStars.splice(index,1);

        }

    });

    requestAnimationFrame(animate);

}

animate();


/* ==========================================
          CURSOR GLOW
========================================== */

const cursor=document.getElementById("cursorGlow");

document.addEventListener("mousemove",(e)=>{

    cursor.style.left=e.clientX+"px";

    cursor.style.top=e.clientY+"px";

});


/* ==========================================
         GLASS PARALLAX
========================================== */

const glass=document.querySelector(".glass");

document.addEventListener("mousemove",(e)=>{

    const x=(e.clientX/window.innerWidth)-0.5;

    const y=(e.clientY/window.innerHeight)-0.5;

    glass.style.transform=`

        rotateY(${x*12}deg)

        rotateX(${-y*12}deg)

        translateY(${Math.sin(Date.now()/700)*5}px)

    `;

});


glass.addEventListener("mouseleave",()=>{

    glass.style.transform="rotateX(0deg) rotateY(0deg)";

});


/* ==========================================
        ELASTIC SVG WAVE
========================================== */

const wave=document.getElementById("wavePath");

let tick=0;

function animateWave(){

    tick+=0.025;

    const p1=160+Math.sin(tick)*18;

    const p2=185+Math.cos(tick*1.4)*20;

    const p3=205+Math.sin(tick*0.9)*18;

    const p4=175+Math.cos(tick*1.7)*20;

    wave.setAttribute(

        "d",

`M0,${p1}
L80,${p2}
C240,${p3}
420,${p4}
620,${p2}
C860,${p1}
1100,${p3}
1280,${p4}
1440,190
L1440,320
L0,320Z`

    );

    requestAnimationFrame(animateWave);

}

animateWave();


/* ==========================================
      FLOATING BLOBS
========================================== */

document.querySelectorAll(".blob").forEach((blob,index)=>{

    let t=index*2;

    function move(){

        t+=0.01;

        blob.style.transform=

        `translate(

        ${Math.sin(t)*35}px,

        ${Math.cos(t)*25}px

        )`;

        requestAnimationFrame(move);

    }

    move();

});


/* ==========================================
       BUTTON GLOW
========================================== */

const btn=document.querySelector(".btn");

setInterval(()=>{

    btn.style.boxShadow=

    `0 0 ${30+Math.random()*30}px rgba(0,212,255,.45)`;

},300);


/* ==========================================
       FADE IN INTRO
========================================== */

window.addEventListener("load",()=>{

    document.body.animate([

        {

            opacity:0,

            filter:"blur(8px)",

            transform:"scale(1.03)"

        },

        {

            opacity:1,

            filter:"blur(0)",

            transform:"scale(1)"

        }

    ],{

        duration:1200,

        easing:"ease-out",

        fill:"forwards"

    });

});


/* ==========================================
       MOBILE PERFORMANCE
========================================== */

if(window.innerWidth<768){

    document.querySelectorAll(".blob").forEach(b=>{

        b.style.filter="blur(45px)";

    });

}


/* ==========================================
      HEADER SCROLL EFFECT
========================================== */

const header=document.querySelector("header");

window.addEventListener("scroll",()=>{

    if(window.scrollY>40){

        header.style.background="rgba(10,15,35,.55)";

        header.style.backdropFilter="blur(18px)";

        header.style.borderBottom="1px solid rgba(255,255,255,.08)";

    }else{

        header.style.background="transparent";

        header.style.backdropFilter="blur(0px)";

        header.style.borderBottom="none";

    }

});


/* ==========================================
        HERO FLOAT
========================================== */

let heroTick=0;

function heroFloat(){

    heroTick+=0.015;

    glass.style.marginTop=

        Math.sin(heroTick)*6+"px";

    requestAnimationFrame(heroFloat);

}

heroFloat();

/* Floating SVG Parallax */

const vectors=document.querySelectorAll(".fv");

document.addEventListener("mousemove",(e)=>{

    const x=(e.clientX/window.innerWidth-.5)*20;

    const y=(e.clientY/window.innerHeight-.5)*20;

    vectors.forEach((v,i)=>{

        v.style.transform+=` translate(${x*(i+1)/6}px,${y*(i+1)/6}px)`;

    });

});
/* ==========================================
        END
========================================== */
