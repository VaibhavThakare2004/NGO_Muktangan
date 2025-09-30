def calculate_indices(hb, rbc, mcv, mch, mchc, rdw):
    mentzer = mcv / rbc if rbc != 0 else 0
    shine_lal = (mcv ** 2 * mch) / 100 if mch != 0 else 0
    srivastava = mch / rbc if rbc != 0 else 0
    green_king = (mcv ** 2 * rdw) / (hb * 100) if hb != 0 else 0
    return round(mentzer,2), round(shine_lal,2), round(srivastava,2), round(green_king,2)

def predict_thalassemia(mentzer, mcv, mch):
    if mentzer < 13 or mcv < 80 or mch < 27:
        return "Likely Thalassemia Minor"
    else:
        return "Not Thalassemia Minor"
