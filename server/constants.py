from rsa import PrivateKey
from datetime import timedelta

IP = '0.0.0.0' 
PORT = 1233
privkey = PrivateKey(278734590028571050727211729267549573308312172917299818710225069363725971781378503666606090888655041562527074655057348316041201487358915779899422083797647063938958917901738110938922956927046151079912877468485054135861157250584514435917, 65537, 85061748334092512848379306122510817800116628139005391980171527339892265981469552669974545947679949208089193782395475245166003189567728902891447916587072585695563646199386217610531479910699364854486773708156286161405832127184412673, 9214735258918953686834090423053075222751191275738159258454941439625375575535283941283844726700644221443876506451496002987521, 30248789812901406505755578106985764291925398337944136477301446386996072643166342268906383981949793124268780877)
delta = {
    'UTC': timedelta(hours=3),
    'DAY': timedelta(days=1),
    'MONTH': timedelta(days=30)
}