import os
import random
import sys
import time
import pygame as pg


WIDTH = 1100  # ゲームウィンドウの幅
HEIGHT = 650  # ゲームウィンドウの高さ
NUM_OF_BOMBS=5 #爆弾の数を表す定数
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    """
    オブジェクトが画面内or画面外を判定し，真理値タプルを返す関数
    引数：こうかとんや爆弾，ビームなどのRect
    戻り値：横方向，縦方向のはみ出し判定結果（画面内：True／画面外：False）
    """
    yoko, tate = True, True
    if obj_rct.left < 0 or WIDTH < obj_rct.right:
        yoko = False
    if obj_rct.top < 0 or HEIGHT < obj_rct.bottom:
        tate = False
    return yoko, tate
class Score:
    def __init__(self):
        self.fonto=pg.font.SysFont("hgp創英角ﾎﾟｯﾌﾟ体", 30)#フォント設定
        self.color=(0,0,255) #青
        self.score=0 #スコアの初期値の設定
        self.img=self.fonto.render(f"score:{str(self.score)}", 0, (0,0,255))#文字列surfaceの作成
        self.img_c = self.img.get_rect()
        self.img_c.center =(100,HEIGHT-50)
    def update(self,screen):
        self.fonto=pg.font.Font(None,30)
        self.img=self.fonto.render(f"score:{str(self.score)}", 0, (0,0,255))#文字列surfaceの作成
        screen.blit(self.img,self.img_c)
def check_bound(beam_instance) -> tuple[bool,bool]:
    #引数　こうかとんrectまたは爆弾rect
    #戻り値:判定結果タプル(横、縦)
    #画面内ならTrue，画面外ならFalse
    yoko,tate=True,True #横方向、縦方向の判定
    #横方向判定
    if beam_instance.left < 0 or WIDTH < beam_instance.right:#画面外だったら
        yoko=False
        #縦方向判定
    if beam_instance.top < 0 or HEIGHT < beam_instance.bottom:#画面内だったら
        tate =False
    return (yoko,tate)        
   
        
    

class Bird:
    """
    ゲームキャラクター（こうかとん）に関するクラス
    """
    delta = {  # 押下キーと移動量の辞書
        pg.K_UP: (0, -5),
        pg.K_DOWN: (0, +5),
        pg.K_LEFT: (-5, 0),
        pg.K_RIGHT: (+5, 0),
    }
    img0 = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    img = pg.transform.flip(img0, True, False)  # デフォルトのこうかとん（右向き）
    imgs = {  # 0度から反時計回りに定義
        (+5, 0): img,  # 右
        (+5, -5): pg.transform.rotozoom(img, 45, 0.9),  # 右上
        (0, -5): pg.transform.rotozoom(img, 90, 0.9),  # 上
        (-5, -5): pg.transform.rotozoom(img0, -45, 0.9),  # 左上
        (-5, 0): img0,  # 左
        (-5, +5): pg.transform.rotozoom(img0, 45, 0.9),  # 左下
        (0, +5): pg.transform.rotozoom(img, -90, 0.9),  # 下
        (+5, +5): pg.transform.rotozoom(img, -45, 0.9),  # 右下
    }

    def __init__(self, xy: tuple[int, int]):
        """
        こうかとん画像Surfaceを生成する
        引数 xy：こうかとん画像の初期位置座標タプル
        """
        self.img = __class__.imgs[(+5, 0)]
        self.rct: pg.Rect = self.img.get_rect()
        self.rct.center = xy

    def change_img(self, num: int, screen: pg.Surface):
        """
        こうかとん画像を切り替え，画面に転送する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 screen：画面Surface
        """
        self.img = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 0.9)
        screen.blit(self.img, self.rct)

    def update(self, key_lst: list[bool], screen: pg.Surface):
        """
        押下キーに応じてこうかとんを移動させる
        引数1 key_lst：押下キーの真理値リスト
        引数2 screen：画面Surface
        """
        sum_mv = [0, 0]
        for k, mv in __class__.delta.items():
            if key_lst[k]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        self.rct.move_ip(sum_mv)
        if check_bound(self.rct) != (True, True):
            self.rct.move_ip(-sum_mv[0], -sum_mv[1])
        if not (sum_mv[0] == 0 and sum_mv[1] == 0):
            self.img = __class__.imgs[tuple(sum_mv)]
        screen.blit(self.img, self.rct)


# ビームクラス:
class Beam:
     """
     こうかとんが放つビームに関するクラス
     """
     def __init__(self, bird:"Bird"):
         """
         ビーム画像Surfaceを生成する
         引数 bird：ビームを放つこうかとん（Birdインスタンス）
        """
         self.img = pg.image.load(f"fig/beam.png")
         self.rct = self.img.get_rect()
         self.rct.centery = bird.rct.centery #bird
         self.rct.left = bird.rct.right
         self.vx, self.vy = +5, 0

     def update(self, screen: pg.Surface):
         """
         ビームを速度ベクトルself.vx, self.vyに基づき移動させる
         引数 screen：画面Surface
         """
         if check_bound(self.rct) == (True, True):
             self.rct.move_ip(self.vx, self.vy)
             screen.blit(self.img, self.rct)    


class Bomb:
    """
    爆弾に関するクラス
    """
    def __init__(self, color: tuple[int, int, int], rad: int):
        """
        引数に基づき爆弾円Surfaceを生成する
        引数1 color：爆弾円の色タプル
        引数2 rad：爆弾円の半径
        """
        self.img = pg.Surface((2*rad, 2*rad))
        pg.draw.circle(self.img, color, (rad, rad), rad)
        self.img.set_colorkey((0, 0, 0))
        self.rct = self.img.get_rect()
        self.rct.center = random.randint(0, WIDTH), random.randint(0, HEIGHT)
        self.vx, self.vy = +5, +5

    def update(self, screen: pg.Surface):
        """
        爆弾を速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        
        yoko, tate = check_bound(self.rct)
        if not yoko:
            self.vx *= -1
        if not tate:
            self.vy *= -1
        self.rct.move_ip(self.vx, self.vy)
        screen.blit(self.img, self.rct)


def main():
    sum_mv = [0, 0]#合計移動量リスト
    pg.display.set_caption("たたかえ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))    
    bg_img = pg.image.load("fig/pg_bg.jpg")
    bird = Bird((300, 200))
    beam=None
    # bomb = Bomb((255, 0, 0), 10)#赤で半径10の円を設置している
    clock = pg.time.Clock()
    tmr = 0
    bombs=[]
    beam_instance=[]
    score=Score()
    for i in range(NUM_OF_BOMBS):
        bombs.append(Bomb((255, 0, 0), 10))
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                 # スペースキー押下でBeamクラスのインスタンス生成
                #  beam = Beam(bird)
                 beam_instance.append(Beam(bird))         
        screen.blit(bg_img, [0, 0])
        # if bomb is not None:
        for bomb in bombs:
                
            if bird.rct.colliderect(bomb.rct):
            # ゲームオーバー時に，こうかとん画像を切り替え，1秒間表示させる
                bird.change_img(8, screen)
                fonto = pg.font.Font(None, 80)
                txt = fonto.render("Game Over", True, (255, 0, 0))
                screen.blit(txt, [WIDTH//2-150, HEIGHT//2])
                pg.display.update()
                time.sleep(1)
                return
        
            
                
            
                
        # if beam is not None:
            # if bomb is not None:
        for j,bomb in enumerate(bombs):
            for a,beam in enumerate(beam_instance):
                if beam is not None:
                    if beam.rct.colliderect(bomb.rct):#ビームと爆弾の衝突関係
                        beam_instance[a]=None #ビームを消す
                        bombs[j]=None #爆弾を消す
                        bird.change_img(6, screen) #喜びエフェクト
                        # bombs[j]=None #爆弾を消す
                        score.score+=1
                        pg.display.update()
                # if beam_instance.colliderect(bomb.rct):#ビームと爆弾の衝突関係
                    

                    
                    bird.change_img(6, screen) 
                beam_instance=[beam for beam in beam_instance if beam is not None]#要素がNoneでないものだけのリスト
        bombs=[bomb for bomb in bombs if bomb is not None]#撃ち落されていない爆弾だけのリスト
            
        key_lst = pg.key.get_pressed()
        bird.update(key_lst, screen)
        if beam is not None:
            beam.update(screen) 
        
        for bomb in bombs: 
            bomb.update(screen)
        for b,beam in enumerate(beam_instance):
            if check_bound(beam.rct) != (True,True):#画面の外だったら
                del beam_instance[b]
            else:
                beam.update(screen)
        score.update(screen)
        pg.display.update()
    
        tmr += 1
        clock.tick(50)
        


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
