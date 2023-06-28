from pydub import AudioSegment


def ogg2wav(ofn):
    wfn = ofn.replace('.ogg', '.wav')
    x = AudioSegment.from_file(ofn)
    x.export(wfn, format='wav')  # maybe use original resolution to make smaller


if __name__ == '__main__':
    ogg2wav('C:\\Users\\Win11\\PycharmProjects\\BetterAlexa\\apps\\discord\\recordings\\test.ogg')
