window.addEventListener('gamepadconnected',event =>{
    console.log('Gamepad connected:')
    console.log(event.gamepad)

})

window.addEventListener('gamepaddisconnected', event => {
    console.log('Gamepad disconnected')
    console.log(event.gamepad)
})

const gamepadDisplay = document.getElementById("gamepad-display")

function update(){
    const gamepads = navigator.getGamepads()
    if(gamepads[0]){
        const gamepadState = {
            id: gamepads[0].id,
            axes : [
                gamepads[0].axes[0].toFixed(2),
                gamepads[0].axes[1].toFixed(2),
                gamepads[0].axes[2].toFixed(2),
                gamepads[0].axes[3].toFixed(2),
            ],
            buttons :[
                {button_0: gamepads[0].buttons[0].pressed},
                {button_1: gamepads[0].buttons[1].pressed},
                {button_2: gamepads[0].buttons[2].pressed},
                {button_3: gamepads[0].buttons[3].pressed},
                {button_4: gamepads[0].buttons[4].pressed},
                {button_5: gamepads[0].buttons[5].pressed},
                {button_6: gamepads[0].buttons[6].pressed},
            ],
        }
        gamepadDisplay.textContent = JSON.stringify(gamepadState, null, 2)
    }
    window.requestAnimationFrame(update)
} 

window.requestAnimationFrame(update)