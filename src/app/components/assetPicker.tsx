import { useState, useEffect } from "react";
import { IoMdArrowDropdown } from "react-icons/io";

interface AssetPickerProps {
  selectedAsset: string | null;
  setSelectedAsset: React.Dispatch<React.SetStateAction<string | null>>;
  assets: { id: string; asset_name: string }[]; 
}

const AssetPicker = ({ selectedAsset, setSelectedAsset, assets }: AssetPickerProps) => {
  const [isDropdownOpen, setDropdownOpen] = useState(false);

  const toggleDropdown = () => {
    setDropdownOpen(!isDropdownOpen);
  };

  const handleAssetSelect = (asset: { id: string; name: string }) => {
    setSelectedAsset(asset.id);  
    setDropdownOpen(false);
  };

  return (
    <div>
      <div className="dropdown">
        <button onClick={toggleDropdown} className="dropbtn">
          {selectedAsset
            ? assets.find((asset) => asset.id === selectedAsset)?.asset_name || "Unknown Asset"
            : "Select an asset"} 
          <IoMdArrowDropdown />
        </button>
        {isDropdownOpen && (
          <div className="dropdown-content">
            {assets.length > 0 ? (
              assets.map((asset) => (
                <a key={asset.id} onClick={() => handleAssetSelect(asset)}>
                  {asset.asset_name}
                </a>
              ))
            ) : (
              <a>No assets available</a>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default AssetPicker;
