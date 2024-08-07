const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

let SCREEN_WIDTH = window.innerWidth;
let SCREEN_HEIGHT = window.innerHeight;
canvas.width = SCREEN_WIDTH;
canvas.height = SCREEN_HEIGHT;

const BLACK = 'black';
const WHITE = 'white';
const RED = 'red';
const GREEN = 'green';
const ORANGE = 'orange';
const BLUE = 'blue';

let BOX_WIDTH = SCREEN_WIDTH / 16;
let BALL_RADIUS = BOX_WIDTH / 5;
const THRESHOLD_DISTANCE = BALL_RADIUS + BOX_WIDTH / 2;

let BOX_INFO = [];
let BALL_LIST = [];
let round = 0;
let mouseClicked = false;
let speedDefined = false;
let ballsAppended = false;
let ballX = SCREEN_WIDTH / 8;
let ballY = SCREEN_HEIGHT * 0.95;
let numberOfBalls = 1;
let lastBallExit = false;
let cosineTheta = 0.6;
let sineTheta = 0.8;
let running = true;
let mouseX, mouseY;

function drawArrow(ctx, fromX, fromY, toX, toY, color) {
    const headlen = BOX_WIDTH / 5;
    const dx = toX - fromX;
    const dy = toY - fromY;
    const angle = Math.atan2(dy, dx);
    ctx.beginPath();
    ctx.moveTo(fromX, fromY);
    ctx.lineTo(toX, toY);
    ctx.strokeStyle = color;
    ctx.lineWidth = 2;
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(toX, toY);
    ctx.lineTo(toX - headlen * Math.cos(angle - Math.PI / 6), toY - headlen * Math.sin(angle - Math.PI / 6));
    ctx.lineTo(toX - headlen * Math.cos(angle + Math.PI / 6), toY - headlen * Math.sin(angle + Math.PI / 6));
    ctx.lineTo(toX, toY);
    ctx.fillStyle = color;
    ctx.fill();
}

function createBoxWithText(boxInfo) {
    ctx.fillStyle = boxInfo[3];
    ctx.strokeStyle = boxInfo[3];
    ctx.lineWidth = 2;
    ctx.strokeRect(boxInfo[0], boxInfo[1], BOX_WIDTH, BOX_WIDTH);
    ctx.font = `${BOX_WIDTH / 2}px Arial`;
    ctx.fillStyle = boxInfo[3];
    ctx.fillText(boxInfo[2], boxInfo[0] + BOX_WIDTH / 2 - BOX_WIDTH / 6, boxInfo[1] + BOX_WIDTH / 2 + BOX_WIDTH / 6);
}

function moreBalls(emptySpaceIndices) {
    const prob = Math.random();
    if (prob < 1 / 3) {
        const amount = Math.floor(Math.random() * 3) + 1;
        const selectedIndices = [];
        for (let i = 0; i < amount; i++) {
            const index = emptySpaceIndices.splice(Math.floor(Math.random() * emptySpaceIndices.length), 1)[0];
            selectedIndices.push(index);
        }
        for (const index of selectedIndices) {
            const thisBallX = index * BOX_WIDTH + BOX_WIDTH / 2;
            const thisBallInfo = [thisBallX, BOX_WIDTH, 1, WHITE];
            ctx.beginPath();
            ctx.arc(thisBallX, BOX_WIDTH * 1.5, BOX_WIDTH / 2, 0, 2 * Math.PI);
            ctx.fillStyle = WHITE;
            ctx.fill();
            BOX_INFO.push(thisBallInfo);
        }
    }
}

function createNewBoxes() {
    const number = Math.floor(Math.random() * 6) + 1;
    const positionIndexList = Array.from({ length: 16 }, (_, i) => i);

    for (let i = 0; i < number; i++) {
        const hitRequired = Math.ceil(Math.sqrt(round)) * 2;
        let color;
        if (hitRequired <= 5) color = GREEN;
        else if (hitRequired <= 20) color = ORANGE;
        else if (hitRequired <= 50) color = BLUE;
        else color = RED;

        const xPosIndex = positionIndexList.splice(Math.floor(Math.random() * positionIndexList.length), 1)[0];
        const xPos = xPosIndex * BOX_WIDTH;
        const yPos = BOX_WIDTH;
        const boxInfo = [xPos, yPos, hitRequired, color];
        createBoxWithText(boxInfo);
        BOX_INFO.push(boxInfo);
    }

    moreBalls(positionIndexList);
}

function moveBoxesDown() {
    for (const box of BOX_INFO) {
        box[1] += BOX_WIDTH;
    }
}

function checkCollision() {
    for (const currentBall of BALL_LIST) {
        const ballRect = { x: currentBall[0] - BALL_RADIUS, y: currentBall[1] - BALL_RADIUS, width: BALL_RADIUS * 2, height: BALL_RADIUS * 2 };

        for (const box of BOX_INFO) {
            const boxRect = { x: box[0], y: box[1], width: BOX_WIDTH, height: BOX_WIDTH };
            if (ballRect.x < boxRect.x + boxRect.width &&
                ballRect.x + ballRect.width > boxRect.x &&
                ballRect.y < boxRect.y + boxRect.height &&
                ballRect.y + ballRect.height > boxRect.y) {
                
                if (box[3] === WHITE) {
                    const index = BOX_INFO.indexOf(box);
                    BOX_INFO.splice(index, 1);
                    return 1;
                } else {
                    const ballCenter = { x: currentBall[0], y: currentBall[1] };
                    const boxCenter = { x: box[0] + BOX_WIDTH / 2, y: box[1] + BOX_WIDTH / 2 };
                    const collisionVector = { x: ballCenter.x - boxCenter.x, y: ballCenter.y - boxCenter.y };

                    if (Math.abs(collisionVector.x) > Math.abs(collisionVector.y)) {
                        currentBall[2] = -currentBall[2];
                    } else {
                        currentBall[3] = -currentBall[3];
                    }

                    box[2] -= 1;
                    if (box[2] <= 0) {
                        const index = BOX_INFO.indexOf(box);
                        BOX_INFO.splice(index, 1);
                    }
                    return 0;
                }
            }
        }
    }
    return 0;
}

function gameLoop() {
    if (!running) return;

    ctx.clearRect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT);

    if (BOX_INFO.length === 0) {
        round += 1;
        ballX = Math.random() * (SCREEN_WIDTH - BOX_WIDTH) + BOX_WIDTH / 2;
        ballY = SCREEN_HEIGHT * 0.95;
        createNewBoxes();
    }

    if (BOX_INFO[0][1] + BOX_WIDTH >= SCREEN_HEIGHT) {
        running = false;
    }

    if (!mouseClicked) {
        const magMouseToBall = Math.sqrt((mouseX - ballX) ** 2 + (mouseY - ballY) ** 2);

        sineTheta = (mouseY - ballY) / magMouseToBall;
        cosineTheta = (mouseX - ballX) / magMouseToBall;
        if (Math.asin(sineTheta) > 0) sineTheta = -sineTheta;

        const magPointer = BOX_WIDTH * 2;
        const dx = magPointer * cosineTheta;
        const dy = magPointer * sineTheta;
        drawArrow(ctx, ballX, ballY, ballX + dx, ballY + dy, 'green');
    } else if (mouseClicked && !speedDefined) {
        ballSpeedX = 20 * cosineTheta;
        ballSpeedY = 20 * sineTheta;
        speedDefined = true;
    }

    if (mouseClicked) {
        if (!ballsAppended) {
            for (let n = 0; n < numberOfBalls; n++) {
                ballX -= 2 * n * ballSpeedX;
                ballY -= 2 * n * ballSpeedY;
                BALL_LIST.push([ballX, ballY, ballSpeedX, ballSpeedY]);
            }
            ballsAppended = true;
        }

        let zeros = 0;
        for (const ball of BALL_LIST) {
            ball[0] += ball[2];
            ball[1] += ball[3];

            if (lastBallExit) {
                if (ball[1] >= SCREEN_HEIGHT - BALL_RADIUS) {
                    ball[2] = 0;
                    ball[3] = 0;
                }
                if (ball[2] === 0) zeros += 1;
                if (ball[3] === 0) zeros += 1;
                if (ball[0] - BALL_RADIUS <= 0 || ball[0] + BALL_RADIUS >= SCREEN_WIDTH) {
                    ball[2] = -ball[2];
                }
                if (ball[1] - BALL_RADIUS <= 0) {
                    ball[3] = -ball[3];
                }
            }

            ctx.beginPath();
            ctx.arc(ball[0], ball[1], BALL_RADIUS, 0, 2 * Math.PI);
            ctx.fillStyle = RED;
            ctx.fill();
        }

        if (BALL_LIST[BALL_LIST.length - 1][1] <= SCREEN_HEIGHT - BALL_RADIUS) {
            lastBallExit = true;
        }

        if (zeros === BALL_LIST.length * 2 && zeros !== 0) {
            round += 1;
            BALL_LIST = [];
            moveBoxesDown();
            createNewBoxes();
            ballX = Math.random() * SCREEN_WIDTH;
            ballY = SCREEN_HEIGHT * 0.95;
            mouseClicked = false;
            speedDefined = false;
            ballsAppended = false;
            lastBallExit = false;
        }
    }

    for (const box of BOX_INFO) {
        if (box[3] !== WHITE) {
            ctx.strokeStyle = box[3];
            ctx.lineWidth = 2;
            ctx.strokeRect(box[0], box[1], BOX_WIDTH, BOX_WIDTH);
            createBoxWithText(box);
        } else {
            ctx.beginPath();
            ctx.arc(box[0], box[1] + BOX_WIDTH / 2, BOX_WIDTH / 2.5, 0, 2 * Math.PI);
            ctx.fillStyle = WHITE;
            ctx.fill();
        }
    }

    if (checkCollision() === 1) {
        numberOfBalls += 1;
    }

    requestAnimationFrame(gameLoop);
}

canvas.addEventListener('mousedown', () => {
    mouseClicked = true;
});

canvas.addEventListener('mousemove', (event) => {
    mouseX = event.clientX - canvas.getBoundingClientRect().left;
    mouseY = event.clientY - canvas.getBoundingClientRect().top;
});

window.addEventListener('resize', () => {
    SCREEN_WIDTH = window.innerWidth;
    SCREEN_HEIGHT = window.innerHeight;
    canvas.width = SCREEN_WIDTH;
    canvas.height = SCREEN_HEIGHT;
    BOX_WIDTH = SCREEN_WIDTH / 16;
    BALL_RADIUS = BOX_WIDTH / 5;
});

gameLoop();
