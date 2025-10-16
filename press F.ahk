; F key spam script
SpamDelay := 30  ; ms between presses (lower = faster spam)

; Special handling for F key to allow spamming while holding
$F::
    ; Send the first F press immediately
    SendInput, f
    
    ; Start a timer to check if key is still being held
    SetTimer, CheckFHeld, 700
return

CheckFHeld:
    if GetKeyState("F", "P") {
        ; If F is still being held, send more F keypresses
        SendInput, f
        Sleep, %SpamDelay%
    } else {
        ; If F is released, stop the timer
        SetTimer, CheckFHeld, Off
    }
return

; When F key is released, ensure the timer is stopped
$F Up::
    SetTimer, CheckFHeld, Off
return
