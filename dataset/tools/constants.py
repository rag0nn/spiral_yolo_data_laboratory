label_dict = {
    0:"Tasit",
    1:"Insan",
    2:"UAP",
    3:"UAI",
    4:"BILINMIYOR"
}

label_color_dict = {
    0:(191,44,123),
    1:(0,109,255),
    2:(255,242,40),
    3:(40,40,255),
    4:(0,0,255)
}

label_color_dict_with_hex = {
          0:"#7b2cbf",
          1:"#ff6d00",
          2:"#28f2ff",
          3:"#ff2828",
          4:"#ff0000"
}

landing_status_color_dict = {
          -1:(255,255,255), # Park Yeri değil
          0:(0,0,255), # Park yeri ama uygun değil
          1:(0,255,100) # Park yeri ve uygun
}

landing_status_dict = {
          -1:"inis alani degil", # Park Yeri değil
          0:"inis alani-uygun degil", # Park yeri ama uygun değil
          1:"inis alani-uygun" # Park yeri ve uygun        
}