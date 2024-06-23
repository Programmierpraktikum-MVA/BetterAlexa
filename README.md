# BetterAlexa Gruppe C 2024  -  Spotify

Jede Endpoint-Funktion in spotifyextenstion.py hat
1. eine plain Version (nimmt acc token + ggf. extra parameter)
2. eine user_... Version (nimmt user identifier (email, ID oä (string)) + ggf. extra parameter)


die user_ version öffnet falls der user nicht zu finden ist die flask app zum login und speichert
die corresponding info in der database (mit hilfsfunktionen).

falls der access_token alt ist, wird die info noch refreshed und neu gespeichert

anschließend nutzt user_... die zugehörige plain funktion

die plain funktion ist ein einfach API CALL an spotify 
