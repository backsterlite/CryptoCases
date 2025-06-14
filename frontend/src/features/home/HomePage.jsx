import React, { useEffect } from 'react';
import Carousel from '../../common/components/Carousel';
import CaseCard from '../cases/components/CaseCard';

export default function MainPage() {


  return (
    <div className="bg-gradient-to-b from-gray-100 via-white to-gray-100 min-h-screen flex flex-col items-center p-4">

      <div className="w-full my-4">
        <Carousel />
      </div>

      <div className="w-full flex-1">
      </div>
    </div>
  );
}