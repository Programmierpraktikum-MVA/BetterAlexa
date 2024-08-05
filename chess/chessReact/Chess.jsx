
import { useEffect, useState } from 'react';
import io from 'socket.io-client';
//import axios from 'axios';
import './chess.css';
import whitePawn from './assets/whitePawn.png';
import blackPawn from './assets/blackPawn.png';
import whiteRook from './assets/whiteRook.png';
import blackRook from './assets/blackRook.png';
import whiteKnight from './assets/whiteKnight.png';
import blackKnight from './assets/blackKnight.png';
import whiteBishop from './assets/whiteBishop.png';
import blackBishop from './assets/blackBishop.png';
import whiteQueen from './assets/whiteQueen.png';
import blackQueen from './assets/blackQueen.png';
import whiteKing from './assets/whiteKing.png';
import blackKing from './assets/blackKing.png';




const vAxis = ["1", "2", "3", "4", "5", "6", "7", "8"];
const hAxis = ["a", "b", "c", "d", "e", "f", "g", "h"];

const socket = io('http://127.0.0.1:5000');



export default function Chess () {
    const [data, setData] = useState('');

    useEffect(() => {
        socket.on('connect', () => {
            console.log('Connected to the server');
        });

        socket.on('update', (data) => {
            console.log('Received update:', data);
            setData(data.message);
        });

        return () => {
            socket.off('connect');
            socket.off('update');
        };
    }, []);

    function piece(p) {
        if (p == "p") {
            return <img className="piece" src={blackPawn}></img>
        }
        if (p == "r") {
            return <img className="piece" src={blackRook}></img>
        }
        if (p == "n") {
            return <img className="piece" src={blackKnight}></img>
        }
        if (p == "b") {
            return <img className="piece" src={blackBishop}></img>
        }
        if (p == "q") {
            return <img className="piece" src={blackQueen}></img>
        }
        if (p == "k") {
            return <img className="piece" src={blackKing}></img>
        }

        if (p == "P") {
            return <img className="piece" src={whitePawn}></img>
        }
        if (p == "R") {
            return <img className="piece" src={whiteRook}></img>
        }
        if (p == "N") {
            return <img className="piece" src={whiteKnight}></img>
        }
        if (p == "B") {
            return <img className="piece" src={whiteBishop}></img>
        }
        if (p == "Q") {
            return <img className="piece" src={whiteQueen}></img>
        }
        if (p == "K") {
            return <img className="piece" src={whiteKing}></img>
        }

        
    }
    function placeFen(fen) {        

        let board = [];
        let k = 0;
        for(let j = hAxis.length-1; j > -1; j--) {
            for(let i = 0; i < hAxis.length; i++) {
                if ((i+ j) % 2 == 0) {
                    board.push(<div key={`${8*i + j}`} className="black-block">
                        {hAxis[i]}{vAxis[j]} 
                        {piece(fen[k])}
                        </div>);
                }
                else {
                    board.push(<div key={`${8*i + j}`} className="white-block">{hAxis[i]}{vAxis[j]} 
                    {piece(fen[k])}</div>);
                }
                k++;
            }
        }
        return(board); 
    }
    
    return <>
        <div className="chessBoard">{placeFen(data)}</div>
    </>
}