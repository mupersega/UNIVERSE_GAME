from class_game import Game
import pygame
import threading


threads = []

if __name__ == '__main__':
    game = Game()
    game_thread = threading.Thread(target=game.mainloop())
    threads.append(game_thread)
    game_thread.start()
