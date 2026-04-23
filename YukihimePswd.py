import tkinter as tk
from tkinter import ttk
from dataclasses import dataclass, fields, asdict

# 1. データの定義
@dataclass
class SystemData:
    ID:         int = 0
    stage:      int = 2
    player:     int = 0
    flag1:      int = 0
    flag2:      int = 0

    #version: int = 0
    p_used:     int = 0

    @classmethod
    def empty(cls):
        empty_params = {f.name: 0 for f in fields(cls)}
        return cls(**empty_params)

@dataclass
class PlayerData:
    live:       int = 2
    MHP:        int = 8
    HP:         int = 8
    money:      int = 0
    weapon:     int = 0
    jyutu:      int = 0
    scroll:     int = 0
    jyutu1:     int = 0
    jyutu2:     int = 0
    jyutu3:     int = 0
    jyutu4:     int = 0
    bomb:       int = 0
    helmet1:    int = 0
    helmet2:    int = 0
    helmet3:    int = 0
    armor1:     int = 0
    armor2:     int = 0
    armor3:     int = 0
    waraji:     int = 1
    food1:      int = 0
    food2:      int = 0
    food3:      int = 0
    tegata:     int = 0
    dictionary: int = 0
    korezou1:   int = 0
    korezou2:   int = 0
    korezou3:   int = 0
    korezou4:   int = 0

    @classmethod
    def empty(cls):
        params = {f.name: 0 for f in fields(cls)}
        return cls(**params)

    @classmethod
    def fullPower(cls):
        data = PlayerData(
            money=0x99999, live=15, HP=16, weapon=2, 
            scroll=9, bomb=0x30, MHP=16,
            jyutu=0x10, jyutu1=1, jyutu2=1, jyutu3=1, jyutu4=1,
            helmet1=24, helmet2=18, helmet3=12, 
            armor1=24, armor2=18, armor3=12, waraji=10,
            food1=3, food2=3, food3=3,
            tegata=1, dictionary=1, korezou1=1, korezou2=1, korezou3=1, korezou4=1
        )
        return data

    @classmethod
    def counterStop(cls):
        data = PlayerData(
            money=0xFFFFF, live=15, HP=31, weapon=3, 
            scroll=15, bomb=0x3F, MHP=31,
            jyutu=0x1F, jyutu1=1, jyutu2=1, jyutu3=1, jyutu4=1,
            helmet1=255, helmet2=255, helmet3=255, 
            armor1=255, armor2=255, armor3=255, waraji=255,
            food1=255, food2=255, food3=255,
            tegata=1, dictionary=1, korezou1=1, korezou2=1, korezou3=1, korezou4=1
        )
        return data

def GetSystemLayout():
    return [
        ("ID",          6,  6),
        ("stage",      12,  4),
        ("p_used",     16,  2),
        ("flag1",      18,  4),
        ("player",     22,  2),
        ("flag2",      24,  4),
    ]

def GetPlayerLayout():
    return [
        ("money",       0, 20),
        ("live",       20,  4),
        ("HP",         24,  5),
        ("scroll",     29,  4),
        ("bomb",       33,  6),
        ("MHP",        39,  5),
        ("jyutu",      44,  5),
        ("jyutu1",     49,  1),
        ("jyutu2",     50,  1),
        ("jyutu3",     51,  1),
        ("jyutu4",     52,  1),
        ("helmet1",    53,  8),
        ("helmet2",    61,  8),
        ("helmet3",    69,  8),
        ("armor1",     77,  8),
        ("armor2",     85,  8),
        ("armor3",     93,  8),
        ("waraji",    101,  8),
        ("food1",     109,  8),
        ("food2",     117,  8),
        ("food3",     125,  8),
        ("tegata",    133,  1),
        ("dictionary",134,  1),
        ("korezou1",  135,  1),
        ("korezou2",  136,  1),
        ("korezou3",  137,  1),
        ("korezou4",  138,  1),
        ("weapon",    139,  2),
    ]

def BuildBitBuffer(sysData: SystemData, playerData: PlayerData) -> int:
    systemLayout = GetSystemLayout()
    playerLayout = GetPlayerLayout()

    error_message = ""
    if(sysData.flag1 > 7):
        error_message = "シナリオフラグが8以上です。恐らく不正なパスワードになります"
    elif(sysData.stage == 9 and sysData.flag1 > 5):
        error_message = "ステージ9且つシナリオフラグが6以上です。恐らくフリーズします"

    bit_buffer = 0
    checksum = 0
    length = len(playerData) * 24+ 3
    bit_buffer |= length     # 文字数
    bit_buffer |= 7 << 6 # マジックナンバー7

    currentOffset = 0
    for name, offset, width in systemLayout:
        value = getattr(sysData, name)
        value &= (1 << width) - 1
        bit_buffer |= (value << (offset + currentOffset))
        v_tmp = value
        while v_tmp > 0:
            checksum += v_tmp & 0xFFFF
            v_tmp //= 0x10000

    currentOffset = 30
    for player in playerData:
        for name, offset, width in playerLayout:
            value = getattr(player, name)
            value &= (1 << width) - 1
            bit_buffer |= (value << (offset + currentOffset))
            v_tmp = value
            while v_tmp > 0:
                checksum += v_tmp & 0xFFFF
                v_tmp //= 0x10000
        currentOffset += 144
    checksum_low = checksum & 63
    checksum_hi = checksum // 256 & 63
    bit_buffer |= checksum_low << currentOffset
    bit_buffer |= checksum_hi << (currentOffset + 6)
    return bit_buffer, error_message

def BitReverse(n):
    return ((n & 1) << 5) | ((n & 2) << 3) | ((n & 4) << 1) | ((n & 8) >> 1) | ((n & 16) >> 3) | ((n & 32) >> 5)

def GetNullPassword(version):
    if version == 0:
        return [
            0o52, 0o25, 0o04, 0o02, 0o00,
            0o02, 0o52, 0o00, 0o04, 0o16,
            0o00, 0o02, 0o50, 0o00, 0o04,
            0o06, 0o31, 0o00, 0o77, 0o77,
            0o20, 0o34, 0o00, 0o04, 0o36,
            0o00, 0o04, 0o40, 0o00, 0o05,
            0o42, 0o00, 0o04, 0o44, 0o00,
            0o06, 0o52, 0o00, 0o05, 0o70,
            0o00, 0o05, 0o72, 0o00, 0o01,
            0o26, 0o00, 0o01, 0o30, 0o00,
            0o01, 0o32, 0o00, 0o01, 0o34,
        ]
    else:
        return [
            0o52, 0o25, 0o04, 0o02, 0o00,
            0o02, 0o52, 0o00, 0o04, 0o16,
            0o00, 0o02, 0o50, 0o00, 0o04,
            0o66, 0o31, 0o00, 0o77, 0o77,
            0o20, 0o34, 0o00, 0o04, 0o36,
            0o00, 0o04, 0o40, 0o00, 0o05,
            0o42, 0o00, 0o04, 0o44, 0o00,
            0o06, 0o52, 0o00, 0o05, 0o30,
            0o00, 0o05, 0o32, 0o00, 0o01,
            0o06, 0o00, 0o01, 0o10, 0o00,
            0o01, 0o12, 0o00, 0o01, 0o14,
        ]

def GetKanaTable():
    return (
        "あいうえおかきく"
        "けこさしすせそた"
        "ちつてとなにぬね"
        "のはひふへほまみ"
        "むめもやゆよわら"
        "りるれろがぎぐげ"
        "ござじずぜぞだぢ"
        "づでどぱぴぷぺぽ"

        "ぁぃぅぇぉかきく"
        "けこさしすせそた"
        "ちってとなにぬね"
        "のはひふへほまみ"
        "むめもゃゅょゎら"
        "りるれろがぎぐげ"
        "ござじずぜぞだぢ"
        "づでどばびぶべぼ"

        "んー"
    )
# US版
'''
"BDGHJQRT"
"VWbdghjq"
"rtvw0123"
"4!\"^♡+=>"
"?@KLMNPX"
"YZ#$klmn"
"pxyz%&56"
"789-/:;<"
'''

def GetKana(n):
    kana = GetKanaTable()
    return kana[n]

def GetCharBits(password):
    kana = GetKanaTable()
    e = ""
    bits = []
    for char in password:
        if char in kana:
            index = kana.index(char)
            if index >= 64:
                index %= 64
                e += char
            bits.append(index)
    return bits, e


def BitToPassword(bit_buffer, id, version, playerNum):
    nullPassword = GetNullPassword(version)
    password = ""
    passLength = playerNum * 24 + 7
    for i in range(passLength):
        char_bit = (bit_buffer >> (i * 6)) & 63
        if i > 1 and i < passLength - 2:
            char_bit = BitReverse(char_bit)
        char =  ((char_bit + id) & 63) ^ nullPassword[i]
        password += GetKana(char)
        if i < passLength - 1:
            if i % 15 == 14: password += "\n"
            elif i % 5 == 4: password += "　"
    return password

def PasswordToBitBuffer(password, version):
    nullPassword = GetNullPassword(version)
    bits = 0
    errors = []
    char_bits, e1 = GetCharBits(password)
    if e1 != "":
        kana = GetKanaTable()
        e2 = ""
        e3 = ""
        for char in e1:
            if char in kana:
                index = kana.index(char)
                if index >= 128:
                    e3 += char
                elif index >= 64:
                    index %= 64
                    e2 += kana[index]
        if e3 != "":
            errors.append(f"「{e3}」は使えません")
            return 0, " / ".join(errors) if errors else None
        elif e2 != "":
            errors.append(f"「{e1}」を「{e2}」と解釈します")

    if len(char_bits) == 31:
        dataLength = 27
    elif len(char_bits) == 55:
        dataLength = 51
    else:
        errors.append(f"31文字/45文字のパスワード限定です。入力：{len(char_bits)}文字")
        return 0, " / ".join(errors) if errors else None

    id = ((char_bits[1] ^ nullPassword[1]) + 57) & 63

    passwordsize = ((char_bits[0] ^ nullPassword[0]) + 64 - id) & 63
    if passwordsize != dataLength:
        errors.append("1文字目か2文字目が異常です")
        return 0, " / ".join(errors) if errors else None

    for i in range(2, dataLength + 2):
        char_bit = ((char_bits[i] ^ nullPassword[i]) + 64 - id) & 63
        char_bit = BitReverse(char_bit) # データ部分はビットを反転する
        bits |= char_bit << (i * 6)
    for i in range(dataLength + 2, dataLength+4):
        char_bit = ((char_bits[i] ^ nullPassword[i]) + 64 - id) & 63
        bits |= char_bit << (i * 6)

    bits |= dataLength
    bits |= id << 6
    return bits, " / ".join(errors)

def BitBufferToSaveData(bitBuffer):
    # (名前, オフセット, ビット幅) の定義
    # 下位ビットから順に記述していくと直感的です
    sysLayout = GetSystemLayout()
    playerLayout = GetPlayerLayout()


    sysData = SystemData.empty()
    playerData=[]

    passLength = bitBuffer & 63
    if passLength == 27:
        playerNum = 1
    else:
        playerNum = 2
    errors = []
    checksum = 0
    currentOffset = 0
    for name, offset, width in sysLayout:
        # ビットからデータを切り出し
        value = bitBuffer >> (offset + currentOffset)
        value &= (1 << width) - 1
        # セーブデータに書く込み
        setattr(sysData, name, value) 
        if name == 'ID': continue # IDはチェックサム解析の対象外
        # 指定位置に詰め込む
        while value > 0:
            checksum += value & 65535
            value //= 65536

    for p in range(playerNum):
        playerData.append(PlayerData.empty())

    currentOffset = 30
    for p in range(playerNum):
        for name, offset, width in playerLayout:
            # ビットからデータを切り出し
            value = bitBuffer >> (offset + currentOffset)
            value &= (1 << width) - 1
            # セーブデータに書く込み
            setattr(playerData[p], name, value) 
            if name == 'ID': continue # IDはチェックサム解析の対象外
            # 指定位置に詰め込む
            while value > 0:
                checksum += value & 65535
                value //= 65536
        currentOffset += 144

    if sysData.player == 0:
        errors.append("参加プレイヤーが0人")
        sysData.player = 0
        sysData.p_used = 0
    elif sysData.player == 3:
        if passLength != 51:
            errors.append("31文字なのに2人")
            sysData.player = 2
            sysData.p_used = 0
        else:
            sysData.player -= 1
    else:
        if passLength != 27:
            errors.append("55文字なのに1人")
            sysData.player = 0
            sysData.p_used = 0
        else:
            sysData.player -= 1

    if sysData.p_used != 0:
        if sysData.p_used + sysData.player != 2:
            errors.append("脱落後フラグが異常")
            sysData.p_used = 0;
        else:
            sysData.p_used = 1;

    if sysData.flag1 > 7:
        errors.append("シナリオフラグが異常")

    if sysData.stage == 0:
        errors.append("ステージ数が異常")
        sysData.stage = 2
    elif sysData.stage < 8:
        sysData.stage += 1
    elif sysData.stage == 8 or sysData.stage > 9:
        errors.append("ステージ数が異常")
        sysData.stage = 9
    else:
        sysData.stage = 9
    #for p in range(playerNum):
    #    if playerData[p].weapon == 3:
    #        errors.append(f"{playerNum + 1}Pの武器が異常")
    #        playerData[p].weapon = 2

    calcchecksum_low = checksum & 63
    calcchecksum_hi = checksum // 256 & 63
    checksum_low = (bitBuffer >> currentOffset) & 63
    checksum_hi = (bitBuffer >> (currentOffset + 6)) & 63
    if(calcchecksum_low != checksum_low or calcchecksum_hi != checksum_hi):
        errors.append("チェックサムが異常")
    return (sysData, playerData), " / ".join(errors)

# --- UI部分 ---

class GeneratorUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ゆき姫 パスワードジェネレータ")
        self.inputs = {}
        
        # 定義情報の整理
        self.rom_options = ["1.0", "1.2"]
        self.hex_fields = ['money', 'bomb', 'jyutu']
        self.bool_fields = ['p_used', 'jyutu1', 'jyutu2', 'jyutu3', 'jyutu4', 'tegata', 'dictionary', 'korezou1', 'korezou2', 'korezou3', 'korezou4']
        self.select_options = {
            'player': ['ゴエモン', 'エビス丸', '2人プレイ'],
            'weapon': [['キセル', '長キセル', 'ヨーヨー', '(小判)'],['笛', '長い笛', 'ピロピロ笛', '(手裏剣)']]
        }

        # 表示名と順序の定義
        self.system_definitions = [
            ("stage", "ステージ (2-9)"), ("player", "プレイヤー"), ("p_used", "2P脱落後"),
            ("flag1", "シナリオフラグ (0-7)"),("flag2", "黄金招き猫 (0-15)"),
        ]
        self.player_definitions = [
            ("live", "残機 (0-15)"), ("MHP", "最大HP (0-31)"), ("HP", "現在HP (0-31)"), ("money", "両 (BCD 0-FFFFF)"),
            ("weapon", "武器"), ("jyutu", "術回数 (BCD 00-1F)"), ("scroll", "巻物 (0-15)"),
            ("jyutu1", "おたすけ"), ("jyutu2", "ひっさつ"), ("jyutu3", "ひこう"), ("jyutu4", "むてき"),
            ("bomb", "爆弾 (BCD 00-3F)"), ("helmet1", "金の兜(耐久値 0-255)"), ("helmet2", "鉄兜"),
            ("helmet3", "かさ"), ("armor1", "金の鎧 "), ("armor2", "かたびら"),
            ("armor3", "みの"), ("waraji", "わらじ(0-255)"), ("food1", "うめおにぎり (0-255)"),
            ("food2", "おにぎり"), ("food3", "ハンバーガー"), ("tegata", "手形"),
            ("dictionary", "辞書"), ("korezou1", "これぞう１"), ("korezou2", "これぞう２"),
            ("korezou3", "これぞう３"), ("korezou4", "これぞう４"),
        ]

        self.setup_ui()
        self.update_player_num()

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="16")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        sysDefault = SystemData()
        playerDefault = PlayerData()
        row, col = 0, 0

        # ID入力欄を先頭に特別配置
        ttk.Label(main_frame, text="生成用ID (0-63)", foreground="blue").grid(row=row, column=col*3, sticky=tk.W, padx=5, pady=2)
        self.id_var = tk.StringVar(value="0")
        ttk.Entry(main_frame, textvariable=self.id_var, width=12).grid(row=row, column=col*3 + 1, sticky=tk.W, padx=5, pady=2)
        row += 1
        # ROMバージョンの選択（Combobox）
        ttk.Label(main_frame, text="ROMバージョン", foreground="blue").grid(row=row, column=col*3, sticky=tk.W, padx=5, pady=2)
        self.rom_version = tk.StringVar(value="1.0") # 初期値を1.0に設定
        rom_combo = ttk.Combobox(main_frame, textvariable=self.rom_version, values=self.rom_options, width=9, state="readonly")
        rom_combo.grid(row=row, column=col*3 + 1, sticky=tk.W, padx=5, pady=2)
        
        row += 1
        for key, label_text in self.system_definitions:
            if key == "ID": continue # IDは上で個別に作成済み
            
            val = getattr(sysDefault, key)
            ttk.Label(main_frame, text=f"{label_text}").grid(row=row, column=col*3, sticky=tk.W, padx=5, pady=2)

            if key in self.bool_fields:
                var = tk.BooleanVar(value=bool(val))
                widget = ttk.Checkbutton(main_frame, variable=var)
                self.inputs[(key, 2)] = ('bool', var, widget)
            elif key in self.select_options:
                var = tk.StringVar(value=self.select_options[key][val])
                widget = ttk.Combobox(main_frame, textvariable=var, values=self.select_options[key], width=9, state="readonly")
                widget.bind("<<ComboboxSelected>>", lambda e: self.update_player_num())
                self.inputs[(key, 2)] = ('select', var, widget)
            else:
                hex_val = hex(val)[2:].upper() if key in self.hex_fields else str(val)
                var = tk.StringVar(value=hex_val)
                widget = ttk.Entry(main_frame, textvariable=var, width=12)
                self.inputs[(key, 2)] = ('hex' if key in self.hex_fields else 'int', var, widget)
            
            widget.grid(row=row, column=col*3 + 1, sticky=tk.W, padx=5, pady=2)
            
            row += 1
            # jyutu4 の後で列を切り替える
            if key == "jyutu4":
                row, col = 0, 1

        for key, label_text in self.player_definitions:
            val = getattr(playerDefault, key)
            ttk.Label(main_frame, text=f"{label_text}").grid(row=row, column=col*3, sticky=tk.W, padx=5, pady=2)

            for p in range(2):
                if key in self.bool_fields:
                    var = tk.BooleanVar(value=bool(val))
                    widget = ttk.Checkbutton(main_frame, variable=var)
                    self.inputs[(key, p)] = ('bool', var, widget)
                elif key in self.select_options:
                    var = tk.StringVar(value=self.select_options[key][p][val])
                    widget = ttk.Combobox(main_frame, textvariable=var, values=self.select_options[key][p], width=9, state="readonly")
                    self.inputs[(key, p)] = ('select', var, widget)
                else:
                    hex_val = hex(val)[2:].upper() if key in self.hex_fields else str(val)
                    var = tk.StringVar(value=hex_val)
                    widget = ttk.Entry(main_frame, textvariable=var, width=12)
                    self.inputs[(key, p)] = ('hex' if key in self.hex_fields else 'int', var, widget)
                
                widget.grid(row=row, column=col*3 + p + 1, sticky=tk.W, padx=5, pady=2)
            
            row += 1
            # jyutu4 の後で列を切り替える
            if key == "jyutu4":
                row, col = 0, 1

        # ボタンとTextエリア（height=3）
        btn = ttk.Button(main_frame, text="初期値", command=self.on_default)
        btn.grid(row=0, column=2, columnspan=1, pady=2, sticky="ew", padx=5)
        btn = ttk.Button(main_frame, text="最強", command=self.on_full)
        btn.grid(row=1, column=2, columnspan=1, pady=2, sticky="ew", padx=5)
        btn = ttk.Button(main_frame, text="カンスト", command=self.on_counterstop)
        btn.grid(row=2, column=2, columnspan=1, pady=2, sticky="ew", padx=5)

        # 解析リザルト
        self.status_var = tk.StringVar(value="たびにっきを入力して解析、または項目を埋めて生成してください")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var, foreground="blue")
        self.status_label.grid(row=18, column=0, columnspan=6, sticky="w")

        # 生成ボタン（左側：0列目から2列分）
        generate_btn = ttk.Button(main_frame, text="↓↓たびにっき生成↓↓", command=self.on_generate)
        generate_btn.grid(row=19, column=0, columnspan=3, pady=20, sticky="ew", padx=20)

        # 解析ボタン（右側：2列目から2列分）
        parse_btn = ttk.Button(main_frame, text="↑↑たびにっき解析↑↑", command=self.on_parse)
        parse_btn.grid(row=19, column=3, columnspan=3, pady=20, sticky="ew", padx=20)

        self.result_text = tk.Text(main_frame, font=("MS Gothic", 18), width=40, height=4, padx=10, pady=10)
        self.result_text.grid(row=20, column=0, columnspan=6, pady=10)

    def on_default(self):
        data = PlayerData()
        self.update_status(data)
        pass

    def on_full(self):
        data = PlayerData.fullPower()
        self.update_status(data)
        pass

    def on_counterstop(self):
        data = PlayerData.counterStop()
        self.update_status(data)
        pass

    def update_status(self, data):
        ignore = ['tegata', 'dictionary', 'korezou1', 'korezou2', 'korezou3', 'korezou4']
        for (key, p), (mode, var, widget) in self.inputs.items():
            if p == 2:
                pass
            elif key in ignore:
                pass
            else:
                val = getattr(data, key)
                if mode == 'bool':
                    var.set(val == 1)
                elif mode == 'select':
                    var.set(self.select_options[key][p][val])
                elif mode == 'hex':
                    var.set(f"{val:X}")
                else:
                    var.set(str(val))

    def update_player_num(self):
        _, _, widget = self.inputs[('player', 2)]
        player_id = widget.current()
        playerNum = 1
        if player_id == 2:
            playerNum = 2
        for (key, p), (mode, var, widget) in self.inputs.items():
            if p == 1:
                if playerNum == 1:
                    widget.configure(state="disabled")
                else:
                    widget.configure(state="normal")
                    if mode == 'select':
                        widget.configure(state="readonly")

    def on_generate(self):
        res = [{},{},{}]
        try:
            id_val = int(self.id_var.get())
        except:
            id_val = 0
        rom_ver = self.rom_options.index(self.rom_version.get())
        for (key, p), (mode, var, widget) in self.inputs.items():
            raw = var.get()
            if mode == 'bool': res[p][key] = 1 if raw else 0
            elif mode == 'select': res[p][key] = widget.current()
            elif mode == 'hex':
                try: res[p][key] = int(raw, 16)
                except: res[p][key] = 0
            else:
                try: res[p][key] = int(raw)
                except: res[p][key] = 0
        res[2]['player'] += 1
        if res[2]['p_used'] > 0:
            res[2]['p_used'] = 3 - res[2]['player']
        if res[2]['stage'] < 2:
            res[2]['stage'] = 1
        elif res[2]['stage'] < 9:
            res[2]['stage'] -= 1
        else:
            res[2]['stage'] = 9
        system = SystemData(**res[2])
        player=[]
        player.append(PlayerData(**res[0]))
        if res[2]['player'] == 3:
            playerNum = 2
            player.append(PlayerData(**res[1]))
        else:
            playerNum = 1
        buffer, e = BuildBitBuffer(system, player)
        password = BitToPassword(buffer, id_val, rom_ver, playerNum)
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert("1.0", password)
        if e == "":
            self.status_label.config(foreground="blue")
            self.status_var.set("成功")
        else:
            self.status_label.config(foreground="orange")
            self.status_var.set(f"異常あり： {e}")
        print(password.replace('\n', '　'))
    
    def on_parse(self):
        password = self.result_text.get("1.0", tk.END).strip()
        bits1, e_char = PasswordToBitBuffer(password, 0)
        if e_char != "" and bits1 == 0:
            self.status_label.config(foreground="red")
            self.status_var.set(f"解析失敗: {e_char}")
        else:
            bits2, e = PasswordToBitBuffer(password, 1)
            data, e = BitBufferToSaveData(bits1)
            data2, e2 = BitBufferToSaveData(bits2)
            version = 0
            if len(e2) == 0:
                data = data2
                e = e2
                version = 1
            elif len(e) == 0:
                pass
            else:
                rom_ver = self.rom_version.get()
                if rom_ver == '1.2':
                    data = data2
                    e = e2
                    version = 1
            if len(e + e_char) > 0:
                self.status_label.config(foreground="orange")
                self.status_var.set(f"一部異常あり: {e} {e_char}")
            else:
                self.status_label.config(foreground="blue")
                self.status_var.set("解析成功")
            sysData = data[0]
            playerData = data[1]
            self.id_var.set(sysData.ID)
            self.rom_version.set(self.rom_options[version])
            for (key, p), (mode, var, widget) in self.inputs.items():
                if p == 2:
                    val = getattr(sysData, key)
                    
                    if mode == 'bool':
                        var.set(val == 1)
                    elif mode == 'select':
                        var.set(self.select_options[key][val])
                    elif mode == 'hex':
                        var.set(f"{val:X}")
                    else:
                        var.set(str(val))
                elif p < len(playerData):
                    val = getattr(playerData[p], key)
                    
                    if mode == 'bool':
                        var.set(val == 1)
                    elif mode == 'select':
                        var.set(self.select_options[key][p][val])
                    elif mode == 'hex':
                        var.set(f"{val:X}")
                    else:
                        var.set(str(val))
            self.update_player_num()

if __name__ == "__main__":
    root = tk.Tk()
    GeneratorUI(root)
    root.mainloop()