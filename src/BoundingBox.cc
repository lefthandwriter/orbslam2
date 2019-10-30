/**
* This file is an extension to ORB-SLAM2.
*
* Copyright (C) 2019 Esther Ling <lingesther at gatech dot edu>
*
* Copyright (C) 2014-2016 Raúl Mur-Artal <raulmur at unizar dot es> (University of Zaragoza)
* For more information see <https://github.com/raulmur/ORB_SLAM2>
*
* ORB-SLAM2 is free software: you can redistribute it and/or modify
* it under the terms of the GNU General Public License as published by
* the Free Software Foundation, either version 3 of the License, or
* (at your option) any later version.
*
* ORB-SLAM2 is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
* GNU General Public License for more details.
*
* You should have received a copy of the GNU General Public License
* along with ORB-SLAM2. If not, see <http://www.gnu.org/licenses/>.
*/


#include "BoundingBox.h"

namespace ORB_SLAM2
{

BoundingBox::BoundingBox()
{
}

BoundingBox::BoundingBox(int x, int y, int width, int height, int id, std::string& frame):bbX(x),bbY(y),bbWidth(width),bbHeight(height),bbId(id),bbFrameNumber(frame)
{
}

void BoundingBox::SetBox(int x, int y, int width, int height, int id, std::string& frame)
{
	bbX = x;
	bbY = y;
	bbWidth = width;
	bbHeight = height;
	bbId = id;
	bbFrameNumber = frame;
}

int BoundingBox::GetX() const
{
	return bbX;
}
int BoundingBox::GetY() const
{
	return bbY;
}
int BoundingBox::GetWidth() const
{
	return bbWidth;
}
int BoundingBox::GetHeight() const
{
	return bbHeight;
}
std::string BoundingBox::GetFrameNumber() const
{
	return bbFrameNumber;
}

} //namespace ORB_SLAM
