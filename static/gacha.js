document.addEventListener("DOMContentLoaded", function() {
    let scene = document.querySelector(".scene");
    let headerLine = document.querySelector("h1");
    let footerLine = document.querySelector("h2");
    let carousel = document.querySelector(".carousel");
    let pokemon = document.querySelectorAll(".carousel__cell");
    let idx = 0;
    let currentBall = pokemon[idx];
    let offset = 1.125;
    //play all automatically when clicked

    //while (idx < pokemon.length) {
    carousel.addEventListener("click", function () {
        
        headerLine.innerText = "";
        footerLine.innerText = "";
        
        let ball = currentBall.firstElementChild;
        let captured = currentBall.lastElementChild;
        let p = currentBall.querySelector("p");
        console.log(p.innerHTML);

        if (currentBall.classList.contains("revealed")) {
            console.log('rotating');
            if (idx >= pokemon.length - 1) {
                console.log('reached the end');
                
                const backlink = document.createElement('a');
                backlink.innerHTML = "<a href='/capture_results'><input type='button' style='position:relative; left:60px; bottom:-60px;' value='Results'></input></a>"
                scene.append(backlink);

            }
            else {
                let angle = idx / pokemon.length * -360 * offset;
                carousel.style.transform = 'rotateY(' + angle + 'deg)';
                
                idx++;
                currentBall = pokemon[idx];
                ball = currentBall.firstElementChild;
                captured = currentBall.lastElementChild;
                p = currentBall.querySelector("p");
            }
        }

        currentBall.classList.add("revealed");

        setTimeout(function () {
            headerLine.innerText = "You got:";
            footerLine.innerText = p.innerHTML;
            //
        }, 4500);

        ball.animate([
            {filter: 'brightness(200%)'},
            {opacity: 0}
        ], {
            duration: 2500, 
            delay: 10,
            iterations: 1,
            fill: 'forwards'
        });

        captured.animate([
            {visibility: 'visible', filter: 'brightness(200%)'},
            {visibility: 'visible', filter: 'brightness(100%)'}
        ], {
            duration: 2000,
            delay: 2500,
            iterations: 1,
            fill: 'forwards'
        });
    
    });
    //}
});