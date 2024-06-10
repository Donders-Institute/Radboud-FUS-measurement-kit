# -*- coding: utf-8 -*-
"""
Copyright (c) 2024 Margely Cornelissen, Stein Fekkes (Radboud University) and Erik Dumont (Image
Guided Therapy)

MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

**Attribution Notice**:
If you use this kit in your research or project, please include the following attribution:
Margely Cornelissen, Stein Fekkes (Radboud University, Nijmegen, The Netherlands) & Erik Dumont
(Image Guided Therapy, Pessac, France) (2024), Radboud FUS measurement kit (version 0.8),
https://github.com/Donders-Institute/Radboud-FUS-measurement-kit
"""

class Scan_Iter:
	def __init__(self, ns,nr,nc, scan='Dir'):
		self.ns = ns
		self.nr = nr
		self.nc = nc
		self.N = ns * nr * nc
		self.cur_index = 0
		self.direct = True if scan=='Dir' else False
		print(f'ns: {self.ns}, nr: {self.nr}, nc: {self.nc}, N: {self.N}, direct: {self.direct}' )

	def __iter__(self):
		'Returns itself as an iterator object'
		return self

	def __next__(self):
		'Returns the next value till current is lower than high'
		if self.cur_index >= self.N:
			raise StopIteration
		else:
			index = self.cur_index
			self.cur_index += 1
			if self.direct:
				return self.dir_i2nsnrnc(index)
			else:
				return self.alt_i2nsnrnc(index)

	def dir_i2nsnrnc(self,i): # Rectangular sequential
		nrnc = self.nr*self.nc
		sl = i // nrnc
		rc = i % nrnc
		row = rc // self.nc
		col = rc % self.nc
		return sl,row,col

	def alt_i2nsnrnc(self,i): # Rectangular alternate
		nrnc = self.nr*self.nc
		sl = i // nrnc
		rc = i % nrnc
		row = rc // self.nc
		rem = rc % self.nc
		if (row % 2 == 0):
			col = rem
		else:
			col = self.nc - rem -1
		return sl,row,col

if __name__ == '__main__':
	myscan_dir = Scan_Iter(3,5,4,scan='Dir')
	i=0
	for s,r,c in myscan_dir:
		print(f'i: {i}, s,r,c: [{s}, {r}, {c}]')
		i+=1
	myscan_alt = Scan_Iter(3,5,4,scan='Alt')
	i=0
	for s,r,c in myscan_alt:
		print(f'i: {i}, s,r,c: [{s}, {r}, {c}]')
		i+=1
