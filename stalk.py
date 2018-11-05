from models import Farmer
def req(returned_values):
    for i in returned_values:
        val = Farmer.query.filter_by(farmer_id  = i).all()
        for v in val:
            v.request_harvest = 1
            db.session.commit()


from models import Job_List
def stalk(j_id, no_bales):
        for j, b in zip(j_id, no_bales):
            print ("job no:",j)
            print ("no of bales: ",b)
            jlist = Job_List.query.filter_by(job_no = j).all()
            for l in jlist:
                l.bails_collected = b
                l.job_complete = 1
                db.session.commit()      
