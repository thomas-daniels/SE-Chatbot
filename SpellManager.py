import pickle
import os.path
from SecretSpells import SecretSpells

class SpellManager:
    
    spellQueue = {}
    earnedSpells = {}
    c = None
    secret_spells = None
    def init(self):
        secret_spells = SecretSpells()
        secret_spells.init()
        if os.path.isfile("earnedSpells.txt"):
            self.load()
            
    def award(self, spell_id, user_id, queue):
        try:
            if queue:
                self.append_to_queue(user_id, spell_id)
            else:
                if spell_id >= len(self.secret_spells.spellList):
                    return "Index out of range."
                if not user_id in self.earnedSpells:
                    self.earnedSpells[user_id] = []
                if not spell_id in self.earnedSpells[user_id]:
                    self.earnedSpells[user_id].append(spell_id)
                    u = self.c.get_user(user_id)
                    n = u.name
                    n = "".join(n.split())
                    self.save()
                    return "Congratulations, @%s, you have earned a new spell: %s" % (n, self.secret_spells.spellList[spell_id])
                return "This spell was already awarded."
        except IndexError:
            return "Index out of range."
        except:
            return "Error"
        
    def remove(self, user_id, spell):
        if user_id in self.earnedSpells:
            if spell in self.earnedSpells[user_id]:
                self.earnedSpells[user_id].remove(spell)
    
    def save(self):
        with open("earnedSpells.txt", "w") as f:
            pickle.dump(self.earnedSpells, f)
        
    def load(self):
        with open("earnedSpells.txt", "r") as f:
            self.earnedSpells = pickle.load(f)
            
    def get_spell_by_index(self, i):
        return self.secret_spells.spellList[i]
    
    def view_spells(self, user_id):
        u = self.c.get_user(user_id)
        n = u.name
        if not user_id in self.earnedSpells:
            return "%s has not earned any spells yet." % n
        else:
            spell_names = map(self.get_spell_by_index, self.earnedSpells[user_id])
            spell_names_str = ", ".join(spell_names)
            return "%s has earned the following spells: %s" % (n, spell_names_str)

    def check_spells(self, event):
        for m in self.secret_spells.spellMethods:
            m(event)
    
    def append_to_queue(self, user, spell):
        if not user in self.spellQueue:
            self.spellQueue[user] = {}
        self.spellQueue[user][spell] = True
        return "Spell added to queue."
    
    def empty_queue(self):
        ret = []
        for user in self.spellQueue.iterkeys():
            for key, value in self.spellQueue[user].iteritems():
                if value == True:
                    ret.append(self.award(key, user, False))
        return ret
        