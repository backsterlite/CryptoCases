import React from 'react';
import { NavLink } from 'react-router-dom';
import { PlayIcon, HomeIcon, ProfileIcon } from '../../assets/navbar-icons';

export default function NavBar() {
  const actions = [
    { url: '/',  svg: <HomeIcon />},
    { url: '/play', svg: <PlayIcon/>  },
    { url: '/profile', svg: <ProfileIcon />},
  ];
  let baseClasses = "just flex flex-1 flex-col items-center justify-end gap-1 rounded-full text-white";
  let activeClass = " text-white";
  let inActiveClass = " text-[#b89d9f]"
  return (
      <>
        <div className={"w-full flex gap-2 border-t border-[#382929] bg-[#261c1c] px-4 pb-3 pt-2"}>
          {actions.map((item, i) => {
            return (
              <NavLink
                key={i}
                to={item.url}
                className={({isActive}) => isActive ? baseClasses + activeClass : baseClasses + inActiveClass}
              >
                <div className="text-white flex h-8 items-center justify-center" data-icon="House" data-size="24px" data-weight="fill">
                  {item.svg}
                </div>
              </NavLink>
            )
          })}
            
        </div>
        <div className="h-5 bg-[#261c1c]"></div>
      </>
  );
}